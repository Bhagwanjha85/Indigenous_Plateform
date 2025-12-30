USER_AVATAR = "images/user.png"
BOT_AVATAR = "images/bot.png"


import streamlit as st
import requests
import re
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Indigenous India Chatbot", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* { font-family: 'Poppins', sans-serif; 
            }

.stApp {
    background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a472a);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

                      
.main .block-container {
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 2.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.main-header {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    padding: 1rem;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
    border-radius: 14px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
}

.main-header h2 {
    color: #ffffff !important;
    font-size: 2.0rem;
    font-weight: 700;
    text-shadow: 3px 3px 10px rgba(0,0,0,0.6);
    margin: 0;
}

.main-header p {
    margin: 0.5rem 0 0 0;
    color: #fef3c7;
    font-size: 1rem;
}

.stChatMessage[data-testid="chat-message-user"] {
    background: rgba(251, 191, 36, 0.2) !important;
    border-radius: 20px 20px 5px 20px;
    margin: 1.5rem 0 1.5rem 3rem;
    padding: 1.5rem;
    border: 1px solid #fbbf24;
    font-size: 13px;
        
}

.stChatMessage[data-testid="chat-message-user"] * {
    color: #ffffff !important;
    font-weight: 500;
}

.stChatMessage[data-testid="chat-message-assistant"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px 20px 20px 5px;
    margin: 1.5rem 3rem 1.5rem 0;
    padding: 1.5rem;
    border-left: 5px solid #10b981;
}

.stChatMessage[data-testid="chat-message-assistant"] * {
    color: #ffffff !important;
    font-weight: 400;
    line-height: 1.7;
    font-size: 14px;  

}

.highlight {
    background: transparent;
    color: #fbf6f6ff;   /* soft indigo */
    font-style: italic;
    font-weight: 900;
}


.stChatInput input {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 2px solid #fbbf24 !important;
    color: white !important;
    border-radius: 25px;
    padding: 12px 20px !important;
}

.stChatInput input::placeholder { color: #cbd5e1; }

.wiki-source {
    background: rgba(16, 185, 129, 0.1);
    border-left: 4px solid #10b981;
    padding: 12px 15px;
    border-radius: 10px;
    color: white;
    margin: 8px 0;
}

.wiki-source a {
    color: #fbbf24 !important;
    text-decoration: none;
    font-weight: 600;
}

.wiki-source small {
    color: #cbd5e1;
    display: block;
    margin-top: 5px;
    font-size: 0.85rem;
}

.status-box {
    background: rgba(16, 185, 129, 0.2);
    border-left: 5px solid #10b981;
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin: 15px 0;
}

.error-box {
    background: rgba(239, 68, 68, 0.2);
    border-left: 5px solid #ef4444;
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin: 15px 0;
}

.image-box {
    background: rgba(139, 92, 246, 0.2);
    border-left: 5px solid #8b5cf6;
    padding: 15px;
    border-radius: 15px;
    color: white;
    margin: 15px 0;
}

.stButton button {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(251, 191, 36, 0.5);
}

.stSidebar {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}

.uploaded-image {
    border-radius: 12px;
    border: 2px solid #fbbf24;
    max-width: 300px;
    margin: 10px 0;
}

@media (max-width: 768px) {
    .stChatMessage[data-testid="chat-message-user"],
    .stChatMessage[data-testid="chat-message-assistant"] {
        margin-left: 0.5rem;
        margin-right: 0.5rem;
    }
    .main-header h2 { font-size: 1.0rem; }
}
</style>
""", unsafe_allow_html=True)

# ========================================
# CHATBOT IDENTITY & MISSION
# ========================================

CHATBOT_IDENTITY = {
    "name": "INDILANG Chatbot",
    "owner": "Bhagwan Ji Jha",
    "owner_education": "B.Tech, Government Engineering College Ajmer",
    "owner_location": "Currently in New Delhi, Hometown: Madhubani, Bihar",
    "mission": "Help tribal peoples and all Indians learn about Indigenous languages, culture, and knowledge",
    "purpose": "Make Wikimedia knowledge accessible in simple words in Indian languages",
    "sources": "Wikipedia, Wikicommons, Wikibooks, Wikisource, Wikinews, Wikidata, Wiktionary, Wikiquotes",
    "specialty": "Indigenous & Tribal languages of India - Santali, Gondi, Kurukh, Khasi, Bhojpuri, Maithili and 20+ Indian languages",
    "style": "Simple, easy-to-understand explanations in user's own language"
}

SYSTEM_CONTEXT = f"""
You are {CHATBOT_IDENTITY['name']}, created by {CHATBOT_IDENTITY['owner']} 
(B.Tech, computer science student | Currently located in New Delhi | Hometown: Madhubani, Bihar).

========================
CRITICAL IDENTITY RULES
========================
- Your creator and owner is ONLY {CHATBOT_IDENTITY['owner']}
- You are INDILANG Chatbot created by Bhagwan Ji Jha
- NEVER say you are Qwen, Alibaba, Alibaba Cloud, or any other company
- If asked about identity, ONLY mention the above facts

========================
YOUR ROLE & EXPERTISE
========================
You are an **Indian Knowledge, Culture, Regional & Current Affairs Assistant**.

Your expertise includes:

1. Indian Culture & Heritage
- Indigenous and tribal languages of India
- Ancient Indian civilizations (Indus Valley, Harappa, Vedic period)
- Indian traditions, customs, festivals, folk arts, architecture, and heritage
- Religions and philosophies originating or practiced in India

2. Regional & Local India Knowledge
- All Indian States, Union Territories, Districts, towns, and villages
- Local cultures, dialects, foods, festivals, clothing, and traditions
- Famous places, temples, monuments, rivers, forts, and tourist spots
- Regional crafts, agriculture, occupations, and lifestyles

3. Indian Society & History
- Evolution of Indian society from ancient to modern times
- Tribal communities and indigenous groups
- Indian freedom movement, reformers, and cultural icons

4. Popular Personalities
- Historical and modern Indian personalities
- Leaders, scientists, artists, writers, sportspersons, activists
- Regionally famous and locally respected figures

5. Politics & Governance (Neutral & Informative)
- Indian politics: Central, State, District, Panchayat, Municipal levels
- Current political events in India
- Government schemes, policies, and administration
- Global political events when relevant to India

6. Current Affairs
- Latest happenings in India and the world
- Social, political, cultural, scientific, environmental updates
- India’s role in global and regional affairs

7. Language Translation and Grammars
- Translate into any language like translate hindi ti bengali, bengali to hindi, hindi to english, english to hindi, english to telugu, tamil, hindi to telugu, tamil, telugu to tamil , hindi, english etc... as per user questions 
- solve the hindi , english , telugu, tamil, maithili, gondi, santhali, nepali, sanskrit, urdu and all indigenous languages grammars, vocabulary, dictionary, errors and more 


========================
SCOPE LIMIT
========================
- If a question is completely unrelated to India, Indian society, wikipedia pages, culture,games,business, poetess, politics, technology or current affairs,
  politely say it is outside your scope.

========================
YOUR MISSION
========================
Help tribal peoples and all Indians understand languages, history, culture, regions, villages, districts,
states, traditions, and current affairs in **simple words**, using Wikimedia sources
(Wikipedia, Wikibooks, Wikisource, Wikinews, Wikidata, Wiktionary, Wikiquote, Wikicommons).

========================
RESPONSE STYLE
========================
- Use SIMPLE, clear language
- Explain difficult terms in easy words
- Be culturally respectful and neutral
- Prefer Indian context and examples
- NO emojis or decorative symbols
- Answer in the user’s selected language

========================
RESPONSE RULES..
========================
IMPORTANT RESPONSE RULES:
- NEVER stop in the middle of a sentence or list
- Always complete sentences before ending the response
- If output length is reaching the limit, summarize and end properly
- Always end with a short concluding line

"""


OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_VISION_MODEL = "moondream"  # Vision model for images (1.7GB)

# Available text models
AVAILABLE_MODELS = {
    "qwen2.5:0.5b": {
        "name": "Qwen 0.5B (Ultra Fast)",
        "size": "0.4GB",
        "speed": "Fastest",
        "quality": "Good",
        "description": "Selected Model is best for quick responses"
    },
    "qwen2.5:3b": {
        "name": "Qwen 3B (Balanced)",
        "size": "1.9GB",
        "speed": "Fast",
        "quality": "Excellent",
        "description": "Selected Model is best for accurate answers"
    }
}

# Default model
DEFAULT_MODEL = "qwen2.5:0.5b"

WIKIMEDIA_PROJECTS = {
    "wikipedia": {"url": "wikipedia.org", "name": "Wikipedia", "desc": "Encyclopedia"},
    "wiktionary": {"url": "wiktionary.org", "name": "Wiktionary", "desc": "Dictionary"},
    "wikiquote": {"url": "wikiquote.org", "name": "Wikiquote", "desc": "Quotes"},
    "wikibooks": {"url": "wikibooks.org", "name": "Wikibooks", "desc": "Textbooks"},
    "wikinews": {"url": "wikinews.org", "name": "Wikinews", "desc": "News"},
    "wikivoyage": {"url": "wikivoyage.org", "name": "Wikivoyage", "desc": "Travel"},
    "wikisource": {"url": "wikisource.org", "name": "Wikisource", "desc": "Texts"}
}

LANGUAGES = {
    "English": {
        "welcome": f" Namaste! I'm {CHATBOT_IDENTITY['name']}. Here is to help peoples to learn about Indigenous languages, culture, and traditions through Wikimedia sources.\n\nAsk me anything about Indigenous languages (Santali, Gondi, Kurukh, maithili, telugu, tamil, bhojpuri, Khasi, etc.), tribal culture, history, traditions and more.. - in your own language! \n\nYou can also upload images and ask questions.",
        "placeholder": "Ask Question(s)",
        "searching": "Searching... please wait",
        "sources": "Wikimedia Sources:",
        "wiki_code": "en",
        "connected": "Connected",
        "disconnected": "Not Running",
        "clear_chat": "Clear Chat",
        "upload_image": "Upload Image",
        "analyzing_image": "Analyzing image..."
    },
    "हिन्दी (Hindi)": {
        "welcome": f" नमस्ते! मैं {CHATBOT_IDENTITY['name']} हूं. मेरा मकसद है आदिवासी लोगों और सभी भारतीयों को उनकी भाषा, संस्कृति और परंपराओं के बारे में आसान शब्दों में बताना।\n\nमुझसे सांताली, गोंडी, कुड़ुख, खासी जैसी आदिवासी भाषाओं, संस्कृति, इतिहास के बारे में पूछें! चित्र भी अपलोड कर सकते हैं। ",
        "placeholder": "आदिवासी भाषा, संस्कृति, इतिहास के बारे में पूछें...",
        "searching": "विकिमीडिया स्रोतों में खोज रहे हैं...",
        "sources": "विकिमीडिया स्रोत:",
        "wiki_code": "hi",
        "connected": "जुड़ा हुआ",
        "disconnected": "नहीं चल रहा",
        "clear_chat": "साफ़ करें",
        "upload_image": " चित्र अपलोड करें",
        "analyzing_image": "चित्र का विश्लेषण..."
    },
    "বাংলা (Bengali)": {
        "welcome": "নমস্কার! আমি আপনার উইকিমিডিয়া সহায়ক। আদিবাসী ভাষা, ইতিহাস, সংস্কৃতি সম্পর্কে প্রশ্ন করুন! ছবিও আপলোড করতে পারেন।",
        "placeholder": "আপনার প্রশ্ন টাইপ করুন বা ছবি আপলোড করুন...",
        "searching": "চিন্তা করছি... অপেক্ষা করুন",
        "sources": "সূত্র:",
        "wiki_code": "bn",
        "connected": "সংযুক্ত",
        "disconnected": "চলছে না",
        "clear_chat": "পরিষ্কার করুন",
        "upload_image": " ছবি আপলোড করুন",
        "analyzing_image": "ছবি বিশ্লেষণ করা হচ্ছে..."
    },
    "தமிழ் (Tamil)": {
        "welcome": "வணக்கம்! நான் உங்கள் விக்கிமீடியா உதவியாளர். பழங்குடி மொழிகள், வரலாறு, கலாச்சாரம் பற்றி கேளுங்கள்! படங்களையும் பதிவேற்றலாம்.",
        "placeholder": "உங்கள் கேள்வியை தட்டச்சு செய்யுங்கள் அல்லது படத்தை பதிவேற்றவும்...",
        "searching": "சிந்தித்து வருகிறது... காத்திருக்கவும்",
        "sources": "ஆதாரங்கள்:",
        "wiki_code": "ta",
        "connected": "இணைக்கப்பட்டது",
        "disconnected": "இயங்கவில்லை",
        "clear_chat": "அழி",
        "upload_image": " படம் பதிவேற்று",
        "analyzing_image": "படத்தை பகுப்பாய்வு செய்கிறது..."
    },
    "తెలుగు (Telugu)": {
        "welcome": "నమస్కారం! నేను మీ వికీమీడియా సహాయకుడిని। గిరిజన భాషలు, చరిత్ర, సంస్కృతి గురించి అడగండి! చిత్రాలను కూడా అప్‌లోడ్ చేయవచ్చు.",
        "placeholder": "మీ ప్రశ్నను టైప్ చేయండి లేదా చిత్రాన్ని అప్‌లోడ్ చేయండి...",
        "searching": "ఆలోచిస్తోంది... దయచేసి వేచి ఉండండి",
        "sources": "మూలాలు:",
        "wiki_code": "te",
        "connected": "కనెక్ట్ చేయబడింది",
        "disconnected": "రన్ కావడం లేదు",
        "clear_chat": "క్లియర్ చేయండి",
        "upload_image": " చిత్రం అప్‌లోడ్",
        "analyzing_image": "చిత్రాన్ని విశ్లేషిస్తోంది..."
    }
}

LANGUAGES.update({
    "मराठी (Marathi)": {
        "welcome": "नमस्कार! मी तुमचा विकिमीडिया सहाय्यक आहे. प्रश्न विचारा किंवा चित्र अपलोड करा!",
        "placeholder": "प्रश्न टाइप करा किंवा चित्र अपलोड करा...",
        "searching": "शोधत आहे... कृपया प्रतीक्षा करा",
        "sources": "स्रोत:",
        "wiki_code": "mr",
        "connected": "जोडलेले",
        "disconnected": "चालू नाही",
        "clear_chat": "साफ करा",
        "upload_image": " चित्र अपलोड",
        "analyzing_image": "चित्र विश्लेषण..."
    },
    "ગુજરાતી (Gujarati)": {
        "welcome": "નમસ્તે! હું તમારો વિકિમીડિયા સહાયક છું. પ્રશ્ન પૂછો અથવા ચિત્ર અપલોડ કરો!",
        "placeholder": "પ્રશ્ન ટાઇપ કરો અથવા ચિત્ર અપલોડ કરો...",
        "searching": "શોધી રહ્યા છીએ... રાહ જુઓ",
        "sources": "સ્રોતો:",
        "wiki_code": "gu",
        "connected": "કનેક્ટેડ",
        "disconnected": "ચાલુ નથી",
        "clear_chat": "સાફ કરો",
        "upload_image": " ચિત્ર અપલોડ",
        "analyzing_image": "ચિત્ર વિશ્લેષણ..."
    },
    "ਪੰਜਾਬੀ (Punjabi)": {
        "welcome": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ ਵਿਕੀਮੀਡੀਆ ਸਹਾਇਕ ਹਾਂ। ਸਵਾਲ ਪੁੱਛੋ ਜਾਂ ਤਸਵੀਰ ਅੱਪਲੋਡ ਕਰੋ!",
        "placeholder": "ਸਵਾਲ ਟਾਈਪ ਕਰੋ ਜਾਂ ਤਸਵੀਰ ਅੱਪਲੋਡ ਕਰੋ...",
        "searching": "ਖੋਜ ਰਿਹਾ ਹੈ... ਉਡੀਕ ਕਰੋ",
        "sources": "ਸਰੋਤ:",
        "wiki_code": "pa",
        "connected": "ਕਨੈਕਟ ਹੈ",
        "disconnected": "ਚੱਲ ਨਹੀਂ ਰਿਹਾ",
        "clear_chat": "ਸਾਫ਼ ਕਰੋ",
        "upload_image": " ਤਸਵੀਰ ਅੱਪਲੋਡ",
        "analyzing_image": "ਤਸਵੀਰ ਵਿਸ਼ਲੇਸ਼ਣ..."
    },
    "മലയാളം (Malayalam)": {
        "welcome": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ വിക്കിമീഡിയ സഹായിയാണ്. ചോദ്യം ചോദിക്കുക അല്ലെങ്കിൽ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക!",
        "placeholder": "ചോദ്യം ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക...",
        "searching": "തിരയുന്നു... കാത്തിരിക്കുക",
        "sources": "ഉറവിടങ്ങൾ:",
        "wiki_code": "ml",
        "connected": "ബന്ധിപ്പിച്ചു",
        "disconnected": "പ്രവർത്തിക്കുന്നില്ല",
        "clear_chat": "മായ്ക്കുക",
        "upload_image": " ചിത്രം അപ്‌ലോഡ്",
        "analyzing_image": "ചിത്രം വിശകലനം..."
    },
    "ಕನ್ನಡ (Kannada)": {
        "welcome": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ವಿಕಿಮೀಡಿಯಾ ಸಹಾಯಕ. ಪ್ರಶ್ನೆ ಕೇಳಿ ಅಥವಾ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ!",
        "placeholder": "ಪ್ರಶ್ನೆ ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ...",
        "searching": "ಹುಡುಕುತ್ತಿದೆ... ನಿರೀಕ್ಷಿಸಿ",
        "sources": "ಮೂಲಗಳು:",
        "wiki_code": "kn",
        "connected": "ಸಂಪರ್ಕಿತ",
        "disconnected": "ಚಾಲನೆಯಲ್ಲಿಲ್ಲ",
        "clear_chat": "ತೆರವುಗೊಳಿಸಿ",
        "upload_image": " ಚಿತ್ರ ಅಪ್‌ಲೋಡ್",
        "analyzing_image": "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ..."
    },
    "ଓଡ଼ିଆ (Odia)": {
        "welcome": "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର ଉଇକିମିଡ଼ିଆ ସହାୟକ। ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ କିମ୍ବା ଛବି ଅପଲୋଡ଼ କରନ୍ତୁ!",
        "placeholder": "ପ୍ରଶ୍ନ ଟାଇପ୍ କରନ୍ତୁ କିମ୍ବା ଛବି ଅପଲୋଡ଼ କରନ୍ତୁ...",
        "searching": "ଖୋଜୁଛି... ଅପେକ୍ଷା କରନ୍ତୁ",
        "sources": "ଉତ୍ସ:",
        "wiki_code": "or",
        "connected": "ସଂଯୁକ୍ତ",
        "disconnected": "ଚାଲୁନାହିଁ",
        "clear_chat": "ସଫା କରନ୍ତୁ",
        "upload_image": " ଛବି ଅପଲୋଡ଼",
        "analyzing_image": "ଛବି ବିଶ୍ଳେଷଣ..."
    },
    "اردو (Urdu)": {
        "welcome": "السلام علیکم! میں آپ کا ویکی میڈیا معاون ہوں۔ سوال پوچھیں یا تصویر اپ لوڈ کریں!",
        "placeholder": "سوال ٹائپ کریں یا تصویر اپ لوڈ کریں...",
        "searching": "تلاش کر رہے ہیں... انتظار کریں",
        "sources": "ذرائع:",
        "wiki_code": "ur",
        "connected": "منسلک",
        "disconnected": "چل نہیں رہا",
        "clear_chat": "صاف کریں",
        "upload_image": " تصویر اپ لوڈ",
        "analyzing_image": "تصویر کا تجزیہ..."
    },
    "मैथिली (Maithili)": {
        "welcome": "प्रणाम! हम अहाँक विकिमीडिया सहायक छी। प्रश्न पुछू वा चित्र अपलोड करू!",
        "placeholder": "प्रश्न टाइप करू वा चित्र अपलोड करू...",
        "searching": "खोजि रहल छी... प्रतीक्षा करू",
        "sources": "स्रोत:",
        "wiki_code": "mai",
        "connected": "जुड़ल अछि",
        "disconnected": "नहि चलि रहल",
        "clear_chat": "साफ करू",
        "upload_image": " चित्र अपलोड",
        "analyzing_image": "चित्र विश्लेषण..."
    },
    "ᱥᱟᱱᱛᱟᱲᱤ (Santali)": {
        "welcome": "ᱡᱚᱦᱟᱨ! ᱤᱧ ᱫᱚ ᱟᱢᱟᱜ ᱣᱤᱠᱤᱢᱤᱰᱤᱭᱟ ᱜᱚᱲᱚᱭᱤᱡ। ᱠᱩᱞᱤ ᱢᱮ ᱟᱨᱵᱟᱝ ᱪᱤᱛᱟᱹᱨ ᱞᱟᱫᱮ ᱢᱮ!",
        "placeholder": "ᱠᱩᱞᱤ ᱴᱟᱭᱤᱯ ᱢᱮ ᱟᱨᱵᱟᱝ ᱪᱤᱛᱟᱹᱨ ᱞᱟᱫᱮ ᱢᱮ...",
        "searching": "ᱥᱮᱸᱫᱽᱨᱟ ᱠᱟᱱᱟ... ᱛᱟᱹᱠᱩ ᱢᱮ",
        "sources": "ᱥᱨᱚᱛ:",
        "wiki_code": "sat",
        "connected": "ᱡᱚᱲᱟᱣ ᱠᱟᱱᱟ",
        "disconnected": "ᱵᱟᱝ ᱪᱟᱹᱞᱩ",
        "clear_chat": "ᱯᱷᱟᱨᱪᱟ ᱢᱮ",
        "upload_image": " ᱪᱤᱛᱟᱹᱨ ᱞᱟᱫᱮ",
        "analyzing_image": "ᱪᱤᱛᱟᱹᱨ ᱯᱟᱹᱨᱦᱟᱹᱭ..."
    },
    "भोजपुरी (Bhojpuri)": {
        "welcome": "प्रणाम! हम रउरा के विकिमीडिया सहायक बानी। सवाल पूछीं या तस्वीर अपलोड करीं!",
        "placeholder": "सवाल टाइप करीं या तस्वीर अपलोड करीं...",
        "searching": "खोजत बानी... इंतजार करीं",
        "sources": "स्रोत:",
        "wiki_code": "bh",
        "connected": "जुड़ल बा",
        "disconnected": "ना चलत बा",
        "clear_chat": "साफ करीं",
        "upload_image": " तस्वीर अपलोड",
        "analyzing_image": "तस्वीर विश्लेषण..."
    },
    "অসমীয়া (Assamese)": {
        "welcome": "নমস্কাৰ! মই আপোনাৰ ৱিকিমিডিয়া সহায়ক। প্ৰশ্ন সুধিব বা ছবি আপলোড কৰক!",
        "placeholder": "প্ৰশ্ন টাইপ কৰক বা ছবি আপলোড কৰক...",
        "searching": "সন্ধান কৰি আছে... অপেক্ষা কৰক",
        "sources": "উৎস:",
        "wiki_code": "as",
        "connected": "সংযুক্ত",
        "disconnected": "চলা নাই",
        "clear_chat": "পৰিষ্কাৰ কৰক",
        "upload_image": " ছবি আপলোড",
        "analyzing_image": "ছবি বিশ্লেষণ..."
    },
    "कोंकणी (Konkani)": {
        "welcome": "नमस्कार! हांव तुमचो विकिमीडिया सहाय्यक। प्रस्न पुसा वा चित्र अपलोड करा!",
        "placeholder": "प्रस्न टाइप करा वा चित्र अपलोड करा...",
        "searching": "सोदता... वाट पळया",
        "sources": "स्रोत:",
        "wiki_code": "gom",
        "connected": "जोडल्लें",
        "disconnected": "चालू ना",
        "clear_chat": "साफ करा",
        "upload_image": " चित्र अपलोड",
        "analyzing_image": "चित्र विश्लेषण..."
    },
    "ꯃꯩꯇꯩꯂꯣꯟ (Manipuri)": {
        "welcome": "ꯈꯨꯔꯨꯝꯖꯔꯤ! ꯑꯩꯅꯥ ꯅꯍꯥꯛꯀꯤ ꯋꯤꯀꯤꯃꯤꯗꯤꯌꯥ ꯃꯇꯦꯡ ꯄꯥꯡꯕꯥ ꯑꯣꯏ। ꯍꯪꯒꯗꯕꯅꯤ ꯅꯠꯠꯔꯒꯥ ꯏꯃꯦꯖ ꯊꯥꯒꯗꯕꯅꯤ!",
        "placeholder": "ꯋꯥꯍꯪ ꯍꯪꯒꯗꯕꯅꯤ ꯅꯠꯠꯔꯒꯥ ꯏꯃꯦꯖ ꯊꯥꯒꯗꯕꯅꯤ...",
        "searching": "ꯊꯤꯔꯤ... ꯉꯥꯏꯖꯕꯤꯌꯨ",
        "sources": "ꯍꯧꯔꯀꯐꯝ:",
        "wiki_code": "mni",
        "connected": "ꯁꯝꯅꯔꯦ",
        "disconnected": "ꯆꯠꯄꯥ ꯂꯩꯇꯦ",
        "clear_chat": "ꯁꯦꯡꯗꯣꯀꯎ",
        "upload_image": " ꯏꯃꯦꯖ ꯊꯥꯒꯗꯕꯅꯤ",
        "analyzing_image": "ꯏꯃꯦꯖ ꯌꯦꯡꯁꯤꯅꯕ..."
    },
    "କାଶି (Khasi)": {
        "welcome": "Khublei! Nga dei ka jingpyndonkam Wikimedia. Pyndonkam ba nongthaw ba ki jingsnew!",
        "placeholder": "Pyndonkam ha ka jaka jingsnew ba upload ki jingsnew...",
        "searching": "Ka la dei pyndonkam... lah wait",
        "sources": "Sources:",
        "wiki_code": "en",
        "connected": "Pynjop la",
        "disconnected": "Ym pynrun",
        "clear_chat": "Clear biang",
        "upload_image": " Upload Image",
        "analyzing_image": "Analyzing image..."
    },
    "गोंडी (Gondi)": {
        "welcome": "जोहार! मय तुमार विकिमीडिया सहायक आंव। प्रस्न पुछा वा चित्र अपलोड करा!",
        "placeholder": "प्रस्न टाइप करा वा चित्र अपलोड करा...",
        "searching": "खोजत हंव... इंतजार करा",
        "sources": "स्रोत:",
        "wiki_code": "gon",
        "connected": "जुड़ल हवय",
        "disconnected": "नई चलत",
        "clear_chat": "साफ करा",
        "upload_image": "चित्र अपलोड",
        "analyzing_image": "चित्र विश्लेषण..."
    },
    "कुड़ुख़ (Kurukh)": {
        "welcome": "जोहार! हाऊं तोहार विकिमीडिया सहायक छों। प्रस्न पुछा वा चित्र अपलोड करा!",
        "placeholder": "प्रस्न टाइप करा वा चित्र अपलोड करा...",
        "searching": "खोजत हाऊं... इंतजार करा",
        "sources": "स्रोत:",
        "wiki_code": "kru",
        "connected": "जुड़ा छै",
        "disconnected": "नाय चलत",
        "clear_chat": "साफ करा",
        "upload_image": "चित्र अपलोड",
        "analyzing_image": "चित्र विश्लेषण..."
    }
})

# ========================================
# IMAGE PROCESSING FUNCTIONS
# ========================================

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string with compression"""
    max_size = (800, 800) 
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=85, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_image_with_ollama(image, question, lang_name):
    """Analyze image using Ollama vision model with improved accuracy"""
    try:
        img_base64 = encode_image_to_base64(image)
        
        prompt = f"""Analyze this image carefully and answer the question.

Question: {question}

Please provide a detailed description including:
1. What objects or people you see
2. Colors, text, and important details
3. Context or setting of the image
4. Direct answer to the question

Be specific and descriptive."""

        payload = {
            "model": OLLAMA_VISION_MODEL,
            "prompt": prompt,
            "images": [img_base64],
            "stream": False,  
            "options": {
                "num_predict": 900, 
                "temperature": 0.4, 
                "num_ctx": 2048,     
                "top_p": 0.9,
                "top_k": 50
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, stream=False, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("response", "").strip()
            
            if not result or len(result) < 10:
                return "Unable to analyze image. Please try:\n1. Upload a clearer image\n2. Check if moondream model is properly installed\n3. Restart Ollama: ollama serve"
            
            if lang_name != "English" and "हिन्दी" in lang_name:
                translation_prompt = f"""Translate this English text to simple Hindi:

{result}

Translate in simple Hindi words:"""
                try:
                    translated = get_ollama_response(translation_prompt, "qwen2.5:0.5b")
                    if translated and not translated.startswith("❌"):
                        return translated
                except:
                    pass
            
            return result
            
        elif response.status_code == 404:
            return f"Model '{OLLAMA_VISION_MODEL}' not found.\n\n Install: ollama pull moondream\n\nAfter install, restart Ollama."
        else:
            return f" Error {response.status_code}.\n\n Fix:\n1. Check: ollama serve\n2. Verify: ollama list\n3. Reinstall: ollama pull moondream"
            
    except requests.exceptions.ConnectionError:
        return " Ollama not connected.\n\n Steps:\n1. Open new terminal\n2. Run: ollama serve\n3. Keep it running\n4. Try again"
    except requests.exceptions.Timeout:
        return " Timeout! Vision model is slow.\n\n Solutions:\n1. Wait 60 seconds, try again\n2. Use smaller image (< 1MB)\n3. Restart Ollama\n4. Check system RAM (need 4GB+)"
    except Exception as e:
        return f" Error: {str(e)}\n\n Try:\n1. ollama serve (in new terminal)\n2. ollama pull moondream\n3. Restart computer if needed"

# ========================================
# WIKIMEDIA SEARCH FUNCTIONS
# ========================================
@st.cache_data(ttl=3600)
def search_wikimedia(query, lang_code="en", project="wikipedia", limit=2):
    """Search specific Wikimedia project"""
    url = f"https://{lang_code}.{project}.org/w/api.php"
    
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "utf8": 1,
        "srprop": "snippet|titlesnippet|timestamp"
    }
    
    headers = {'User-Agent': 'AdvancedWikimediaChatbot/2.0'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json().get("query", {}).get("search", [])
    except:
        pass
    return []

def get_wikipedia_summary(title, lang_code="en"):
    """Get detailed Wikipedia article summary"""
    url = f"https://{lang_code}.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts|info",
        "exintro": True,
        "explaintext": True,
        "inprop": "url",
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    return {
                        "extract": page_data.get("extract", ""),
                        "url": page_data.get("fullurl", "")
                    }
    except:
        pass
    return None

def search_all_wikimedia_parallel(query, lang_code="en"):
    """Fast Wikipedia-only search (optimized for speed)"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future = executor.submit(search_wikimedia, query, lang_code, "wikipedia", 1)
        try:
            data = future.result(timeout=5)
            if data:
                results["wikipedia"] = data
        except:
            pass
    
    return results

def check_ollama():
    """Quick Ollama check"""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=1)
        return r.status_code == 200
    except:
        return False

def is_casual_query(query):
    """Detect casual conversation"""
    casual_patterns = [
        r'\b(hi|hello|hey|namaste|namaskar|vanakkam|namaskara|khublei|johar)\b',
        r'\bhow are you\b',
        r'\bwho are you\b',
        r'\bwhat.*your name\b',
        r'\bthanks?\b',
        r'\bbye\b'
    ]
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in casual_patterns)

def highlight_keywords(text):
    """Highlight important words"""
    keywords = [
        r'\b(Wikipedia|Wikimedia|Wiktionary|Wikiquote|Wikibooks|Wikinews|Wikivoyage|Bhagwan Ji Jha |owner|Indigenous Language|Government engineering college Ajmer|INDILANG|wikidata|Madhubani|Bihar|Uttarpradesh|Delhi|Rajasthan|Bhopal|Nepal|America|Mountain|River)\b',
        r'\b(India|Indian|Adivasi|tribal|indigenous|Scheduled Tribes)\b',
        r'\b(festival|culture|heritage|tourism|ganga|yamuna|delhi metro|metro|Buildings)\b',
        r'\b(\d{4}|\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\b',
    ]
    
    highlighted = text
    for pattern in keywords:
        highlighted = re.sub(
            pattern,
            r'<span class="highlight">\g<0></span>',
            highlighted,
            flags=re.IGNORECASE
        )
    return highlighted

def get_ollama_response(prompt, model_name):
    """Optimized streaming with Indigenous India context"""
    try:
        full_prompt = f"""{SYSTEM_CONTEXT}

{prompt}"""
        
        if "0.5b" in model_name:
            settings = {
                "num_predict": 750,
                "num_ctx": 1024,
                "top_p": 0.85,
                "top_k": 25,
                "repeat_penalty": 1.2,
                "temperature": 0.4,
                "num_thread": 4
            }
            timeout = 35
        else:
            settings = {
                "num_predict": 800,
                "temperature": 0.4,
                "num_ctx": 2048,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.15,
                "num_thread": 6
            }
            timeout = 45
        
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": True,
            "options": settings
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=timeout)
        
        if response.status_code == 200:
            full_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            full_text += chunk["response"]
                        if chunk.get("done", False):
                            break
                    except:
                        continue
            return full_text.strip() if full_text else "Unable to generate response."
        elif response.status_code == 404:
            return f" Model '{model_name}' not found!\n\n Install: ollama pull {model_name}"
        else:
            return f" Error {response.status_code}\n\n Check: ollama serve"
            
    except requests.exceptions.Timeout:
        return " Timeout! Model might be loading. Try again."
    except requests.exceptions.ConnectionError:
        return " Ollama not running!\n\n Start: ollama serve"
    except Exception as e:
        return f" Error: {str(e)}"

def build_comprehensive_context(query, lang_code):
    """Fast Wikipedia search with limited results for speed"""
    all_results = search_all_wikimedia_parallel(query, lang_code)
    
    context_parts = []
    sources = []
    
    if "wikipedia" in all_results and all_results["wikipedia"]:
        wiki_result = all_results["wikipedia"][0]
        title = wiki_result.get("title", "")
        summary_data = get_wikipedia_summary(title, lang_code)
        if summary_data:
            extract = summary_data["extract"][:600] 
            context_parts.append(f"{title}: {extract}")
            sources.append({
                "project": "Wikipedia",
                "title": title,
                "url": summary_data["url"],
                "snippet": extract[:120]
            })
    
    return " ".join(context_parts), sources

def get_answer(query, lang_name, wiki_code, model_name, image=None):
    """Generate answers focused on Indigenous India with simple explanations"""
    
    # Image analysis
    if image is not None:
        response = analyze_image_with_ollama(image, query, lang_name)
        return response, []
    
    identity_keywords = ['who are you', 'what is your name', 'who created you', 'who made you', 'your owner', 
                        'your creator', 'who built you','tumko kisne banaya', 'tumhara owner kon hai', 'who developed you',
                        'तुम कौन हो', 'आप कौन हैं', 'तुम्हारा मालिक कौन', 'तुम्हें किसने बनाया',
                        'আপনি কে', 'তুমি কে', 'നിങ്ങൾ ആരാണ്', 'நீங்கள் யார்']
    
    if any(keyword in query.lower() for keyword in identity_keywords):
        if lang_name == "हिन्दी (Hindi)":
            return f"""मैं {CHATBOT_IDENTITY['name']} हूँ।

मेरे मालिक और निर्माता: {CHATBOT_IDENTITY['owner']}
शिक्षा: {CHATBOT_IDENTITY['owner_education']}
स्थान: {CHATBOT_IDENTITY['owner_location']}

मेरा उद्देश्य: आदिवासी लोगों और सभी भारतीयों को उनकी भाषाओं, संस्कृति और परंपराओं के बारे में आसान शब्दों में बताना। मैं विकिपीडिया जैसे विकिमीडिया स्रोतों से जानकारी देता हूँ।

मैं 20+ भारतीय भाषाओं में काम करता हूँ - सांताली, गोंडी, कुड़ुख, खासी, भोजपुरी, मैथिली आदि।""", []
        else:
            return f"""I am {CHATBOT_IDENTITY['name']}.

Owner and Creator: {CHATBOT_IDENTITY['owner']}
Education: {CHATBOT_IDENTITY['owner_education']}
Location: {CHATBOT_IDENTITY['owner_location']}

My Purpose: Help tribal peoples and all Indians learn about Indigenous languages, culture, and traditions in simple words through Wikimedia sources like Wikipedia.

I work in 20+ Indian languages including Bengali, Santali, Tamil, Telugu, Gondi, Kurukh, Khasi, Bhojpuri, Maithili, and more.""", []
    
    if is_casual_query(query):
        prompt = f"{query}\n\nRespond warmly in {lang_name} (1-2 simple sentences). IMPORTANT: You are {CHATBOT_IDENTITY['name']} created by {CHATBOT_IDENTITY['owner']}, NOT Qwen or Alibaba. Never mention Qwen, Alibaba, or any other company."
        response = get_ollama_response(prompt, model_name)
        return response, []
    
    wikimedia_context, sources = build_comprehensive_context(query, wiki_code)
    
    word_limit = "150-200" if "0.5b" in model_name else "200-300"
    
    if wikimedia_context:
        context = wikimedia_context[:600] if "0.5b" in model_name else wikimedia_context[:800]
        prompt = f"""Context from Wikimedia (Wikipedia, Wikibooks, etc.): {context}

Question: {query}

IMPORTANT INSTRUCTIONS:
- You are {CHATBOT_IDENTITY['name']} created by {CHATBOT_IDENTITY['owner']}
- NEVER say you are Qwen, Alibaba Cloud, or any other company
- Explain in SIMPLE, EASY words that anyone can understand
- Focus on Indigenous/Tribal aspects if relevant
- Do NOT use emojis or icons in your answer
- you can provide image in the answer if relevant or user's questions or user can request for image

Provide answer in {lang_name} language ({word_limit} words):
- Use simple vocabulary
- Explain complex terms in easy language
- Include cultural context
- Be respectful of Indigenous communities
- if required as per questions answer all the relevent information that need to user provide it
- No emojis or special characters

Answer:"""
    else:
        prompt = f"""Question: {query}

IMPORTANT INSTRUCTIONS:
- Do NOT use emojis or icons in your answer

Provide answer in {lang_name} language ({word_limit} words):
- Use SIMPLE, EASY words
- Explain clearly for everyone to understand
- Focus on Indigenous/Tribal knowledge if relevant
- Be accurate and respectful
- No emojis or special characters

Answer:"""

    response = get_ollama_response(prompt, model_name)
    
    response = re.sub(r'(?i)(qwen|indiralang|indralang|Indriel|alibaba|alibaba cloud)', CHATBOT_IDENTITY['name'], response)
    
    return response, sources

# ========================================
# UI Sections..
# ========================================

st.sidebar.title("Settings")

st.sidebar.markdown("---")
st.sidebar.markdown("### SELECT MODEL")
selected_model = st.sidebar.selectbox(
    "",
    options=list(AVAILABLE_MODELS.keys()),
    format_func=lambda x: AVAILABLE_MODELS[x]["name"],
    index=0,
    label_visibility="collapsed"
)

model_info = AVAILABLE_MODELS[selected_model]
st.sidebar.markdown(f"""
<div style='background: rgba(139, 92, 246, 0.2); border-left: 4px solid #8b5cf6; padding: 12px; border-radius: 8px; margin-bottom: 15px;'>
    <div style='color: #c4b5fd; font-size: 0.7rem; margin-top: 5px;'>{model_info['description']}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
selected_lang = st.sidebar.selectbox("SELECT LANGUAGE", list(LANGUAGES.keys()), index=0)
ui = LANGUAGES[selected_lang]



st.sidebar.markdown("---")

st.sidebar.markdown(f"### {ui['upload_image']}")
st.sidebar.markdown("<small style='color: #94a3b8;'>Max: 5MB | JPG/PNG</small>", unsafe_allow_html=True)

if 'uploaded_image' in st.session_state:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.markdown(f"<div style='color: #10b981; font-size: 0.85rem;'>Image loaded</div>", unsafe_allow_html=True)
    with col2:
        if st.button("❌", key="remove_img", help="Remove image"):
            if 'uploaded_image' in st.session_state:
                del st.session_state.uploaded_image
            if 'current_image' in st.session_state:
                del st.session_state.current_image
            st.rerun()

uploaded_file = st.sidebar.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="file_uploader")

if uploaded_file:
    try:
        # Check file size
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
        if file_size > 5:
            st.sidebar.error("Image > 5MB! Use smaller image.")
        else:
            image = Image.open(uploaded_file)
            st.sidebar.image(image, caption=f"Size: {file_size:.1f}MB", use_container_width=True)
            st.session_state.current_image = uploaded_file.name
            st.session_state.uploaded_image = image
            st.sidebar.success("Ready! Ask about this image.")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")
elif 'uploaded_image' in st.session_state:
    # Show previously uploaded image
    st.sidebar.image(st.session_state.uploaded_image, caption="Current Image", use_container_width=True)

st.sidebar.markdown("---")

if st.sidebar.button(ui["clear_chat"], use_container_width=True):
    st.session_state.messages = [{"role": "assistant", "content": ui["welcome"]}]
    # Don't clear image on chat clear - only clear on explicit image removal
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style='color: #94a3b8; font-size: 0.8rem; padding: 1rem; text-align: center;'>
    <strong>Created by</strong><br>
    <strong style='color: #fbbf24;'>{CHATBOT_IDENTITY['owner']}</strong><br>
    <a href="https://github.com/Bhagwanjha85/" style="color:green; text-decoration:none; font-size:12px;"> GO TO:__  <mark>[ Github ]</mark></a><br>
</div>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
    <div class="main-header">
        <h2>{CHATBOT_IDENTITY['name'].upper()}</h2>
        <p>Indigenous India Knowledge in 20+ Languages</p>

    </div>
""", unsafe_allow_html=True)

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": ui["welcome"]}]

# Display messages
for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        if "image" in msg and msg["image"]:
            st.image(msg["image"], caption="Uploaded Image", width=300)
        
        if msg["role"] == "assistant":
            highlighted = highlight_keywords(msg["content"])
            st.markdown(highlighted, unsafe_allow_html=True)
        else:
            st.write(msg["content"])
        
        if "sources" in msg and msg["sources"]:
            st.markdown(f"**{ui['sources']}**")
            for src in msg["sources"]:
                project_name = src.get("project", "Wikipedia")
                st.markdown(f"""
                <div class="wiki-source">
                    <strong>{project_name}:</strong> <a href="{src['url']}" target="_blank">{src['title']}</a><br>
                    <small>{src['snippet']}...</small>
                </div>
                """, unsafe_allow_html=True)

# Input section..
if prompt := st.chat_input(ui["placeholder"]):
    current_image = st.session_state.get('uploaded_image', None)
    
    user_msg = {"role": "user", "content": prompt}
    if current_image:
        user_msg["image"] = current_image
        user_msg["has_image"] = True
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user", avatar=USER_AVATAR):
        if current_image:
            st.image(current_image, caption="Question about this image", width=300)
        st.write(prompt)
    
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        status = st.empty()
        
        if current_image:
            status.markdown(f"**{ui['analyzing_image']}**")
            response_text = analyze_image_with_ollama(current_image, prompt, selected_lang)
            sources = []
            
            if not response_text.startswith("❌") and not response_text.startswith(" ") and not response_text.startswith("⏱️"):
                if 'uploaded_image' in st.session_state:
                    del st.session_state.uploaded_image
                if 'current_image' in st.session_state:
                    del st.session_state.current_image
        else:
            status.markdown(f"**{ui['searching']}**")
            response_text, sources = get_answer(prompt, selected_lang, ui["wiki_code"], selected_model, None)
        
        status.empty()
        highlighted = highlight_keywords(response_text)
        st.markdown(highlighted, unsafe_allow_html=True)
        
        if sources:
            st.markdown(f"**{ui['sources']}**")
            for src in sources:
                project_name = src.get("project", "Wikipedia")
                st.markdown(f"""
                <div class="wiki-source">
                    <strong>{project_name}:</strong> <a href="{src['url']}" target="_blank">{src['title']}</a><br>
                    <small>{src['snippet']}...</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "sources": sources
    })
    
    if current_image and not response_text.startswith("❌"):
        st.rerun()