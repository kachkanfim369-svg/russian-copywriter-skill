"""Линтер правил copywriter-a. Проверяет механические правила: длину, эмодзи, переменную имени в посте, штампы, формат чисел.
Не проверяет смысл, орфографию и падежи: их проверяет сам копирайтер вручную."""
import re
EMO=re.compile("[\U0001F300-\U0001FAFF☀-➿]")
NAME=re.compile(r"\{имя\}|%name%|\{name\}|\{\{name\}\}")
SLOP=[r"не просто",r"это не [^.\n]{1,40}, а",r"давайте разберёмся",r"важно отметить",r"уникальн",r"революцион",r"инновацион",
 r"в современном мире",r"данн(ый|ая|ое|ые)\b",r"является",r"в рамках",r"осуществ",r"погруз",r"раскро(й|йте) потенциал",
 r"друзья",r"дорогие мои|дорогая моя|дорогие друзья",r"секрет успеха",r"подписывайтесь",r"ставьте лайк",r"Результат\?",r"А знаете",r"без [^,.\n]{2,25}, без [^,.\n]{2,25}"]
def lint(name,kind,text):
    issues=[]; t=text.strip(); lines=[l for l in t.split("\n")]
    first=next(l for l in lines if l.strip())
    n=len(t); emo=len(EMO.findall(t))
    if kind=="post":
        if NAME.search(t): issues.append("ПОСТ: есть переменная имени")
        if not 300<=n<=1200: issues.append(f"ПОСТ: длина {n} вне 300–1200")
        if emo>3: issues.append(f"ПОСТ: эмодзи {emo}>3")
        if sum(c.isupper() for c in first if c.isalpha())/max(1,sum(c.isalpha() for c in first))>.5: issues.append("ПОСТ: капс в первой строке")
    else:
        if not NAME.search(t): issues.append("РАССЫЛКА: нет имени")
        if not 300<=n<=1300: issues.append(f"РАССЫЛКА: длина {n} вне 300–1300")
        lim=3 if n<500 else (5 if n<900 else 7)
        if emo>lim: issues.append(f"РАССЫЛКА: эмодзи {emo}>{lim}")
        if "👇" not in t and "👉" not in t: issues.append("РАССЫЛКА: нет пальца перед призывом")
    for p in SLOP:
        m=re.search(p,t,re.I)
        if m: issues.append(f"штамп: «{m.group(0)}»")
    if re.search(r"\d\s*₽\b",t) is None and "₽" in t: pass
    if re.search(r"\d₽",t): issues.append("число слитно с ₽")
    if re.search(r"\bм2\b",t): issues.append("м2 вместо м²")
    if re.search(r"\d{4,}(?!\s*[:.,/]|\d)",re.sub(r"\d{1,3}( \d{3})+","",t)) and re.search(r"\b\d{5,}\b",t): issues.append("число 5+ знаков без пробела тысяч")
    if "—" in t and n<800: issues.append("длинное тире в короткой единице: замени запятой, двоеточием или точкой")
    for blk in t.split("\n\n"):
        if len([l for l in blk.split("\n") if l.strip()])>5 and not re.search(r"^\d\.",blk,re.M): issues.append("абзац >5 строк")
    if re.search(r"(?i)перейдите по ссылке|нажмите на ссылку",t): issues.append("CTA не от первого лица/механика ссылки")
    if re.search(r"\b(\w{4,})\b(?:[^.\n]*\b\1\b){2,}",t,re.I): pass
    if "{имя}" in t and re.search(r"(для|с|без|от|к) \{имя\}",t): issues.append("имя в косвенном падеже")
    if "!" in t and t.count("!")>3: issues.append(f"восклицаний {t.count('!')}")
    return issues

if __name__=="__main__":
    import sys
    # usage: python3 lint.py post|mail файл.txt   (или текст из stdin)
    kind=sys.argv[1] if len(sys.argv)>1 else "mail"
    text=open(sys.argv[2]).read() if len(sys.argv)>2 else sys.stdin.read()
    iss=lint("текст",kind,text)
    print("OK" if not iss else "НАЙДЕНО:"); [print(" -",i) for i in iss]
