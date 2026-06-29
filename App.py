# =====================================================================
# SEKCJA 1: IMPORTY BIBLIOTEK
# Pobieramy tu wszystkie niezbędne narzędzia do działania aplikacji.
# =====================================================================
import streamlit as st # Główna biblioteka do tworzenia interfejsu (strony WWW)
import os # Pozwala na operacje systemowe (np. ustawienie klucza API w środowisku)
import uuid # Do generowania unikalnych identyfikatorów (opcjonalnie przydatne w LangChain)
from langchain_google_genai import ChatGoogleGenerativeAI # Łącznik z modelami Google Gemini
from langchain_core.tools import tool # Pozwala tworzyć funkcje (narzędzia) zrozumiałe dla AI
from langchain_community.tools import DuckDuckGoSearchRun # Narzędzie do wyszukiwania w internecie
from langgraph.prebuilt import create_react_agent # Tworzy Agenta, który myśli i używa narzędzi

# =====================================================================
# SEKCJA 2: USTAWIENIA STRONY
# Konfigurujemy podstawowe parametry karty w przeglądarce.
# =====================================================================
st.set_page_config(
    page_title="Wirtualny Trener AI", # Nazwa na karcie w przeglądarce
    page_icon="💪",                   # Ikonka (favicon)
    layout="centered"                 # Aplikacja trzyma się środka ekranu
)

# =====================================================================
# SEKCJA 3: NIESTANDARDOWY CSS (STYLOWANIE)
# Zmieniamy domyślny wygląd Streamlita, aby aplikacja wyglądała nowocześnie.
# Wstrzykujemy kod CSS bezpośrednio na stronę.
# =====================================================================
st.markdown("""
<style>
    /* Zmniejszenie górnego marginesu i ustalenie szerokości kontenera */
    .block-container {
        padding-top: 1.5rem !important; 
        max-width: 850px !important;
    }

    /* Powiększenie zwykłego tekstu, list i opcji wyboru */
    p, li, div[data-baseweb="select"] { font-size: 24px !important; }
    
    /* Powiększenie pytań zadawanych użytkownikowi (etykiety) */
    label p { font-size: 32px !important; font-weight: 600 !important; }
    
    /* GŁÓWNY TYTUŁ - Wyśrodkowanie i animacja pulsowania */
    .main-title {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 15px !important;
        width: 100% !important;
        margin-bottom: 5px !important;
        animation: pulse-animation 2.5s ease-in-out infinite !important;
    }
    
    @keyframes pulse-animation {
        0% { transform: scale(1); }
        50% { transform: scale(1.06); } 
        100% { transform: scale(1); }
    }
    
    /* Ognisty gradient przechodzący przez tekst tytułu */
    .fire-text {
        font-size: 54px !important;
        font-weight: bold !important;
        background: linear-gradient(to top, #ffea00 0%, #ff7300 25%, #ff0000 50%, #ff7300 75%, #ffea00 100%);
        background-size: 100% 200%;
        color: transparent !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        animation: fire-glow 2s linear infinite !important;
        white-space: nowrap !important;
    }

    /* Zabezpieczenie emotki, by nie straciła swoich kolorów */
    .pulse-emoji { font-size: 54px !important; }

    @keyframes fire-glow {
        0% { background-position: 0% 200%; }
        100% { background-position: 0% 0%; }
    }

    /* Wygląd nagłówków w wygenerowanym planie */
    h3, h3 span, h4, h4 span {
        font-size: 32px !important;
        margin-top: 25px !important;
    }

    /* PRZYCISK GŁÓWNY - Parametry i pozycjonowanie */
    div.stButton { margin-top: 45px !important; }
    
    button[data-testid="baseButton-primary"] {
        font-size: 24px !important;
        padding: 8px 20px !important; 
        font-weight: 900 !important;
        position: relative !important;
        overflow: hidden !important; 
        border: none !important;
    }
    
    /* Efekt świetlnej smugi przelatującej przez przycisk */
    button[data-testid="baseButton-primary"]::before {
        content: "" !important;
        display: block !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 50% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent) !important;
        transform: skewX(-20deg) !important;
        animation: sweep-shine 4s infinite !important;
        z-index: 10 !important;
        pointer-events: none !important;
    }

    /* Wymuszenie widoczności tekstu nad blaskiem */
    button[data-testid="baseButton-primary"] p {
        font-size: 24px !important;
        font-weight: 900 !important;
        position: relative !important;
        z-index: 20 !important;
    }

    @keyframes sweep-shine {
        0% { left: -100%; }
        20% { left: 200%; } 
        100% { left: 200%; } 
    }

    /* NAPRAWA SUWAKA - Poprawa odstępów, żeby tekst nie był ucinany */
    div[data-testid="stSlider"] { margin-bottom: -25px !important; }
    div[data-baseweb="slider"] { margin-top: 30px !important; }
    div[data-baseweb="slider"] div { font-size: 20px !important; overflow: visible !important; }

    /* Wygląd "wybranych elementów" w polu wyboru partii */
    span[data-baseweb="tag"], span[data-baseweb="tag"] span { font-size: 18px !important; }
    
    /* Wygląd pola na klucz API */
    input { font-size: 20px !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# SEKCJA 4: NAGŁÓWEK I OPIS
# Generowanie powitalnej części aplikacji widocznej dla użytkownika.
# =====================================================================

# Główny tytuł sformatowany według własnych klas CSS (zamiast standardowego st.title)
st.markdown("""
<div class='main-title'>
    <span class='fire-text'>Wirtualny Trener Personalny</span>
    <span class='pulse-emoji'>💪</span>
</div>
""", unsafe_allow_html=True)

# Opis aplikacji
st.markdown("<p style='text-align: center; margin-top: 10px;'>Wybierz partie mięśniowe oraz liczbę ćwiczeń, a Agent AI ułoży dla ciebie indywidualny plan na następny trening dostosowany do twoich potrzeb.</p>", unsafe_allow_html=True)

# Niewidzialny blok robiący estetyczny odstęp
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
st.divider()

# =====================================================================
# SEKCJA 5: AUTORYZACJA API
# Prosimy użytkownika o podanie klucza Gemini i chowamy znaki (password).
# =====================================================================
api_key = st.text_input("Wklej swój klucz API Gemini:", type="password")

# Jeśli użytkownik wpisał klucz, wykonujemy resztę programu:
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key # Rejestracja klucza w systemie dla LangChain

    # =====================================================================
# SEKCJA 6: DEFINICJA NARZĘDZI DLA AGENTA AI
    # Uczymy Agenta, jak korzystać z lokalnych plików i internetu.
    # =====================================================================
    
    @tool
    def czytaj_baze_cwiczen(zapytanie: str) -> str:
        """Zwraca listę ćwiczeń z lokalnego pliku."""
        try:
            with open("cwiczenia.txt", "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return "Błąd: Brak pliku cwiczenia.txt"

    @tool
    def wyszukiwarka_internetowa(zapytanie: str) -> str:
        """Wyszukuje najnowsze informacje treningowe w internecie."""
        wyszukiwarka = DuckDuckGoSearchRun()
        return wyszukiwarka.run(zapytanie)

    # Pakujemy narzędzia w jedną listę
    tools = [czytaj_baze_cwiczen, wyszukiwarka_internetowa]

    # =====================================================================
    # SEKCJA 7: INICJALIZACJA MODELU I AGENTA
    # Podpinamy "mózg" AI i dajemy mu jego narzędzia.
    # =====================================================================
    
    # Inicjalizacja modelu Gemini (temperature 0.2 oznacza dużą precyzję)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    # Utworzenie agenta potrafiącego logicznie myśleć (ReAct) i używać narzędzi
    agent = create_react_agent(llm, tools=tools)

    st.divider()
    
    # =====================================================================
    # SEKCJA 8: INTERFEJS UŻYTKOWNIKA (PREFERENCJE TRENINGU)
    # Zbieranie danych od użytkownika.
    # =====================================================================
    
    # Wybór partii mięśniowych
    dostepne_partie = ["Klatka piersiowa", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Łydki", "Brzuch"]
    wybrane_partie = st.multiselect("Które partie mięśniowe chcesz trenować?", dostepne_partie)
    
    st.divider()
    
    # Suwak do wyboru liczby ćwiczeń (od 3 do 12)
    liczba_cwiczen = st.slider("Ile ćwiczeń chcesz wykonać?", min_value=3, max_value=12, value=5)

    st.divider()

    # =====================================================================
    # SEKCJA 9: PRZYCISK GENEROWANIA I OBSŁUGA BŁĘDÓW
    # Wyśrodkowanie przycisku za pomocą kolumn i sprawdzenie poprawności.
    # =====================================================================
    
    # Tworzymy 3 kolumny: pusta po lewej, główna w środku, pusta po prawej
    kol1, kol2, kol3 = st.columns([1, 2, 1])
    
    with kol2:
        # Generujemy przycisk
        generuj = st.button("Generuj Plan Treningowy", type="primary", use_container_width=True)

    # Jeśli kliknięto przycisk:
    if generuj:
        # Blokada: Jeśli nie wybrano mięśni, przerwij i pokaż ostrzeżenie
        if not wybrane_partie:
            st.warning("Wybierz przynajmniej jedną partię mięśniową!")
        else:
            
            # =====================================================================
            # SEKCJA 10: KOMUNIKACJA Z AI I GENEROWANIE PLANU
            # Skonstruowanie dokładnego polecenia (promptu) i odpowiedź modelu.
            # =====================================================================
            
            with st.spinner("Agent AI myśli, analizuje plik i przeszukuje internet..."):
                
                # Bardzo precyzyjna instrukcja krok po kroku dla Agenta
                prompt_zadania = f"""
                Zbuduj plan treningowy. Użytkownik chce trenować: {', '.join(wybrane_partie)}. 
                Plan ma mieć dokładnie {liczba_cwiczen} ćwiczeń wyciągniętych z bazy.
                
                KROK 1: Wywołaj 'czytaj_baze_cwiczen' i wybierz odpowiednią liczbę ćwiczeń z pliku zgodnie z zasadami na dole pliku.
                KROK 2: Wywołaj 'wyszukiwarka_internetowa', aby sprawdzić najlepszą liczbę serii i powtórzeń do tych ćwiczeń (na hipertrofię).
                KROK 3: Połącz dane i wypisz W JĘZYKU POLSKIM ostateczny plan.
                
                BEZWZGLĘDNY WYMÓG FORMATOWANIA LISTY ĆWICZEŃ:
                Aby nazwa ćwiczenia była wyraźniejsza i delikatnie większa, dodaj cztery krzyżyki (####) przed numerem każdego ćwiczenia. Serie i powtórzenia zachowaj jako zwykłe podpunkty z myślnikiem. Użyj pogrubień dokładnie tak, jak pokazano poniżej:
                #### 1. **Nazwa ćwiczenia**
                - Liczba serii: **X**
                - Zakres powtórzeń: **Y-Z**
                #### 2. **Nazwa ćwiczenia**
                - Liczba serii: **X**
                - Zakres powtórzeń: **Y-Z**
                
                BEZWZGLĘDNY WYMÓG FORMATOWANIA ANALIZY KOŃCOWEJ:
                Bezpośrednio pod listą ćwiczeń dodaj nagłówek o treści: "### Kilka słów o twoim planie:"
                Pod tym nagłówkiem napisz spersonalizowaną, unikalną analizę stworzonego planu (dokładnie 2-3 zdania). Analiza musi:
                1. Zidentyfikować, do jakiego modelu treningowego pasuje ten zestaw (wybierz i nazwij jeden z nich: Push, Pull, Upper, Lower lub Full Body).
                2. Wyjaśnić logicznie, dlaczego akurat te ćwiczenia zostały dobrane dla wybranych grup mięśniowych (np. dlaczego najpierw wyciskanie, a potem rozpiętki).
                3. Podsumować, dlaczego ten konkretny trening sprawdzi się w praktyce i przyniesie pożądany efekt.
                
                Nie dodawaj żadnych nawiasów kwadratowych ani struktur kodu JSON. Odpowiedź ma być czystym tekstem sformatowanym w Markdown.
                """
                
                try:
                    # Wywołanie agenta (dajemy mu limit 8 kroków na myślenie/szukanie)
                    odpowiedz = agent.invoke({"messages": [("user", prompt_zadania)]}, config={"recursion_limit": 8})
                    st.success("Plan gotowy!")
                    
                    # Wyciągnięcie z odpowiedzi samego tekstu
                    ostateczny_tekst = odpowiedz["messages"][-1].content
                    
                    # Zabezpieczenie formatowania z LangGraph (czasem zwraca listę słowników zamiast tekstu)
                    if isinstance(ostateczny_tekst, list):
                        tekst_do_wyswietlenia = ostateczny_tekst[0].get("text", str(ostateczny_tekst))
                    else:
                        tekst_do_wyswietlenia = ostateczny_tekst
                        
                    # Wyświetlenie gotowego planu na stronie
                    st.markdown(tekst_do_wyswietlenia)
                    
                except Exception as e:
                    # Wychwytywanie ewentualnych błędów (np. problem z internetem API)
                    st.error(f"Wystąpił błąd: {e}")
                    
# (Koniec bloku 'if api_key')
# Jeśli nie podano klucza, pokazujemy prośbę o jego wklejenie
else:
    st.info("Aby rozpocząć, wklej swój klucz API Gemini w polu powyżej.")