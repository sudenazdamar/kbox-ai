import streamlit as st
from core.chat_manager import ChatManager
from database import save_search, get_history, delete_search, clear_history
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
import io
import datetime

st.set_page_config(
    page_title="KBox Al",
    page_icon="⚡",
    layout="wide",
)

if "chat_manager" not in st.session_state:
    st.session_state.chat_manager = ChatManager()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "tr"
if "favorites" not in st.session_state:
    st.session_state.favorites = []

lang = st.session_state.language

TEXTS = {
    "tr": {
        "title": "🎓 Akademik Araştırma Asistanı",
        "caption": "Google Scholar + Groq ile çalışır",
        "memory": "Hafızadaki Mesajlar",
        "clear": "🗑️ Konuşmayı Temizle",
        "settings": "⚙️ Ayarlar",
        "input": "Akademik bir soru sorun...",
        "searching": "🔍 Google Scholar'da aranıyor...",
        "sources": "📚 Kaynakları Gör",
        "citations": "atıf",
        "read": "Makaleyi Oku",
        "download_pdf": "📄 PDF İndir",
        "favorites": "⭐ Favoriler",
        "no_favorites": "Henüz favori eklenmedi.",
        "remove_favorite": "🗑️ Kaldır",
        "pdf_title": "Akademik Araştırma Asistanı - Sohbet Geçmişi",
        "history": "🕐 Geçmiş Aramalar",
        "no_history": "Henüz arama yapılmadı.",
        "clear_history": "🗑️ Geçmişi Temizle",
        "system_prompt": (
            "Sen akademik literatür analizi konusunda uzmanlaşmış bir Akademik Araştırma Asistanısın.\n\n"
            "TEMEL KURALLAR:\n"
            "1. Yalnızca sağlanan araştırma verilerini kullan, asla bilgi uydurma.\n"
            "2. Verilen referans numaralarını kullanarak kaynak göster (ör. [1], [2, 3]).\n"
            "3. Veri yetersizse açıkça belirt: 'Sağlanan kaynaklar bu soruyu yanıtlamak için yeterli değil.'\n"
            "4. Her zaman Türkçe cevap ver.\n\n"
            "CEVAP YAPISI:\n"
            "- 2-3 cümlelik kısa ve doğrudan bir cevapla başla.\n"
            "- Belirli makalelere atıfta bulunarak kanıta dayalı açıklama yap.\n"
            "- Sonda 'Kaynaklar' bölümü ekle.\n\n"
            "ASLA YAPMA:\n"
            "- Yazar adı, yayın yılı veya dergi adı uydurma.\n"
            "- Kaynakların desteklemediği konularda kesinlik iddia etme.\n"
        ),
    },
    "en": {
        "title": "🎓 Academic Research Assistant",
        "caption": "Powered by Google Scholar + Groq",
        "memory": "Messages in Memory",
        "clear": "🗑️ Clear Conversation",
        "settings": "⚙️ Settings",
        "input": "Ask an academic question...",
        "searching": "🔍 Searching Google Scholar...",
        "sources": "📚 View Sources",
        "citations": "citations",
        "read": "Read Paper",
        "download_pdf": "📄 Download PDF",
        "favorites": "⭐ Favorites",
        "no_favorites": "No favorites added yet.",
        "remove_favorite": "🗑️ Remove",
        "pdf_title": "Academic Research Assistant - Chat History",
        "history": "🕐 Search History",
        "no_history": "No searches yet.",
        "clear_history": "🗑️ Clear History",
        "system_prompt": (
            "You are an Academic Research Assistant specializing in scholarly literature analysis.\n\n"
            "CORE RULES:\n"
            "1. Only use the provided research data, never fabricate facts.\n"
            "2. Always cite sources using reference numbers (e.g., [1], [2, 3]).\n"
            "3. If data is insufficient, state: 'The provided sources do not contain enough information.'\n"
            "4. Always respond in English.\n\n"
            "RESPONSE STRUCTURE:\n"
            "- Start with a concise direct answer (2-3 sentences).\n"
            "- Follow with evidence-based elaboration citing specific papers.\n"
            "- End with a References section.\n\n"
            "NEVER:\n"
            "- Invent author names, publication years, or journal names.\n"
            "- Claim certainty beyond what the sources support.\n"
        ),
    },
}

t = TEXTS[lang]

def generate_pdf(messages, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'], fontSize=16, spaceAfter=20)
    user_style = ParagraphStyle(
        'User', parent=styles['Normal'], fontSize=11, spaceAfter=8, spaceBefore=12)
    assistant_style = ParagraphStyle(
        'Assistant', parent=styles['Normal'], fontSize=10, spaceAfter=8)
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(
        f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}",
        styles['Normal']))
    story.append(Spacer(1, 20))
    for msg in messages:
        if msg["role"] == "user":
            story.append(Paragraph(f"<b>Soru:</b> {msg['content']}", user_style))
        else:
            clean = msg["content"].replace('\n', '<br/>')
            story.append(Paragraph(f"<b>Cevap:</b><br/>{clean}", assistant_style))
        story.append(Spacer(1, 10))
    doc.build(story)
    buffer.seek(0)
    return buffer

st.title(t["title"])
st.caption(f"{t['caption']} | {t['memory']}: {st.session_state.chat_manager.message_count}/10")

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(t["sources"]):
                for i, src in enumerate(msg["sources"], 1):
                    col_src, col_fav = st.columns([5, 1])
                    with col_src:
                        st.markdown(f"**[{i}] {src.title}** ({src.year})")
                        st.markdown(f"*{src.authors}* | 📖 {src.citations} {t['citations']}")
                        st.markdown(f"[{t['read']}]({src.link})")
                    with col_fav:
                        if st.button("⭐", key=f"fav_{idx}_{i}"):
                            if src not in st.session_state.favorites:
                                st.session_state.favorites.append(src)
                                st.rerun()

if prompt := st.chat_input(t["input"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(t["searching"]):
            result = st.session_state.chat_manager.ask(prompt, t["system_prompt"])
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander(t["sources"]):
                for i, src in enumerate(result["sources"], 1):
                    col_src, col_fav = st.columns([5, 1])
                    with col_src:
                        st.markdown(f"**[{i}] {src.title}** ({src.year})")
                        st.markdown(f"*{src.authors}* | 📖 {src.citations} {t['citations']}")
                        st.markdown(f"[{t['read']}]({src.link})")
                    with col_fav:
                        if st.button("⭐", key=f"fav_new_{i}"):
                            if src not in st.session_state.favorites:
                                st.session_state.favorites.append(src)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
    save_search(prompt, result["answer"], result["sources"], lang)
    st.rerun()

with st.sidebar:
    st.header(t["settings"])
    if st.button(t["clear"]):
        st.session_state.chat_manager.clear_memory()
        st.session_state.messages = []
        st.rerun()
    st.metric(t["memory"], f"{st.session_state.chat_manager.message_count} / 10")

    if st.session_state.messages:
        pdf_buffer = generate_pdf(st.session_state.messages, t["pdf_title"])
        st.download_button(
            label=t["download_pdf"],
            data=pdf_buffer,
            file_name=f"akademik_arastirma_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )

    st.divider()
    st.subheader(t["favorites"])
    if not st.session_state.favorites:
        st.info(t["no_favorites"])
    else:
        for i, fav in enumerate(st.session_state.favorites):
            st.markdown(f"**{fav.title}** ({fav.year})")
            st.markdown(f"*{fav.authors}*")
            if st.button(t["remove_favorite"], key=f"remove_{i}"):
                st.session_state.favorites.pop(i)
                st.rerun()
            st.divider()

    st.divider()
    st.subheader(t["history"])
    history = get_history()
    if not history:
        st.info(t["no_history"])
    else:
        if st.button(t["clear_history"]):
            clear_history()
            st.rerun()
        for row in history:
            search_id, query, answer, sources, language, created_at = row
            with st.expander(f"🔍 {query[:40]}... ({created_at})"):
                st.markdown(f"**Soru:** {query}")
                st.markdown(f"**Cevap:** {answer[:300]}...")
                if st.button("🗑️ Sil", key=f"del_{search_id}"):
                    delete_search(search_id)
                    st.rerun()

    st.divider()
    st.subheader("🌐 Dil / Language")
    if st.button("🇹🇷 Türkçe", use_container_width=True):
        st.session_state.language = "tr"
        st.session_state.chat_manager.clear_memory()
        st.session_state.messages = []
        st.rerun()
    if st.button("🇬🇧 English", use_container_width=True):
        st.session_state.language = "en"
        st.session_state.chat_manager.clear_memory()
        st.session_state.messages = []
        st.rerun()