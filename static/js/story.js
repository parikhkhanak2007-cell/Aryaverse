document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    // =====================================================
    // STORY ID
    // =====================================================

    const storyId =
        document.body.dataset.storyId;


    console.log(
        "ARYAVERSE STORY PAGE"
    );

    console.log(
        "Story ID:",
        storyId
    );


    if (!storyId) {

        console.error(
            "Story ID missing."
        );

        return;

    }


    // =====================================================
    // ELEMENTS
    // =====================================================

    const languageSelect =
        document.getElementById(
            "languageSelect"
        );

    const translateBtn =
        document.getElementById(
            "translateBtn"
        );

    const translationPanel =
        document.getElementById(
            "translationPanel"
        );

    const translatedStory =
        document.getElementById(
            "translatedStory"
        );

    const translationTitle =
        document.getElementById(
            "translationTitle"
        );

    const translationStatus =
        document.getElementById(
            "translationStatus"
        );

    const closeTranslation =
        document.getElementById(
            "closeTranslation"
        );


    const listenBtn =
        document.getElementById(
            "listenBtn"
        );

    const audioPanel =
        document.getElementById(
            "audioPanel"
        );

    const audioTitle =
        document.getElementById(
            "audioTitle"
        );

    const audioStatus =
        document.getElementById(
            "audioStatus"
        );

    const storyAudio =
        document.getElementById(
            "storyAudio"
        );


    const questionInput =
        document.getElementById(
            "questionInput"
        );

    const askButton =
        document.getElementById(
            "askButton"
        );

    const aiStatus =
        document.getElementById(
            "aiStatus"
        );

    const answerBox =
        document.getElementById(
            "answerBox"
        );


    const likeBtn =
        document.getElementById(
            "likeBtn"
        );

    const likeStatus =
        document.getElementById(
            "likeStatus"
        );


    const commentForm =
        document.getElementById(
            "commentForm"
        );

    const commentName =
        document.getElementById(
            "commentName"
        );

    const commentText =
        document.getElementById(
            "commentText"
        );

    const commentStatus =
        document.getElementById(
            "commentStatus"
        );

    const commentsContainer =
        document.getElementById(
            "commentsContainer"
        );


    // =====================================================
    // HELPERS
    // =====================================================

    function escapeHTML(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }


    function renderText(text, element) {

        if (!element) {
            return;
        }


        element.innerHTML = "";


        const paragraphs =
            String(text || "")
                .replace(/\r/g, "")
                .split(/\n\s*\n/)
                .map(
                    item =>
                        item.trim()
                )
                .filter(Boolean);


        paragraphs.forEach(
            paragraph => {

                const p =
                    document.createElement(
                        "p"
                    );


                p.textContent =
                    paragraph;


                element.appendChild(p);

            }
        );

    }


    function setStatus(
        element,
        message,
        error = false
    ) {

        if (!element) {
            return;
        }


        element.textContent =
            message || "";


        element.classList.toggle(
            "error",
            error
        );

    }


    function setLoading(
        button,
        loading,
        normalText
    ) {

        if (!button) {
            return;
        }


        button.disabled =
            loading;


        button.textContent =
            loading
                ? "PLEASE WAIT..."
                : normalText;

    }


    // =====================================================
    // TRANSLATE
    // =====================================================

    if (translateBtn) {

        translateBtn.addEventListener(
            "click",
            async () => {

                const language =
                    languageSelect?.value ||
                    "en";


                if (language === "en") {

                    setStatus(
                        translationStatus,
                        "English is the original story."
                    );

                    return;

                }


                setLoading(
                    translateBtn,
                    true,
                    "TRANSLATE"
                );


                setStatus(
                    translationStatus,
                    "Translating with Aryaverse AI..."
                );


                try {

                    const response =
                        await fetch(
                            `/api/story/${storyId}/translate`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json",

                                    "Accept":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    language
                                })
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "Translation:",
                        data
                    );


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Translation failed."
                        );

                    }


                    const text =
                        data.text ||
                        data.translated ||
                        data.translated_text ||
                        data.translation;


                    if (!text) {

                        throw new Error(
                            "No translated text returned."
                        );

                    }


                    translationPanel.hidden =
                        false;


                    renderText(
                        text,
                        translatedStory
                    );


                    const languageName =
                        languageSelect.options[
                            languageSelect.selectedIndex
                        ].text;


                    translationTitle.textContent =
                        languageName;


                    setStatus(
                        translationStatus,
                        `Translated to ${languageName}.`
                    );


                }
                catch (error) {

                    console.error(
                        error
                    );


                    setStatus(
                        translationStatus,
                        error.message,
                        true
                    );

                }
                finally {

                    setLoading(
                        translateBtn,
                        false,
                        "TRANSLATE"
                    );

                }

            }
        );

    }


    // =====================================================
    // CLOSE TRANSLATION
    // =====================================================

    if (closeTranslation) {

        closeTranslation.addEventListener(
            "click",
            () => {

                translationPanel.hidden =
                    true;

            }
        );

    }


    // =====================================================
    // TEXT TO SPEECH
    // =====================================================

    if (listenBtn) {

        listenBtn.addEventListener(
            "click",
            async () => {

                const language =
                    languageSelect?.value ||
                    "en";


                setLoading(
                    listenBtn,
                    true,
                    "LISTEN"
                );


                setStatus(
                    audioStatus,
                    "Preparing narration..."
                );


                try {

                    const response =
                        await fetch(
                            `/api/story/${storyId}/tts`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    language
                                })
                            }
                        );


                    const contentType =
                        response.headers.get(
                            "content-type"
                        ) || "";


                    /*
                     * Direct MP3 response
                     */

                    if (
                        contentType.includes(
                            "audio/"
                        )
                    ) {

                        const blob =
                            await response.blob();


                        const url =
                            URL.createObjectURL(
                                blob
                            );


                        storyAudio.src =
                            url;


                        audioPanel.hidden =
                            false;


                        audioTitle.textContent =
                            "Story narration";


                        storyAudio.load();


                        try {

                            await storyAudio.play();

                        }
                        catch {

                            setStatus(
                                audioStatus,
                                "Audio ready. Press play."
                            );

                        }


                        setStatus(
                            audioStatus,
                            "Narration ready."
                        );


                        return;

                    }


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "TTS failed."
                        );

                    }


                    const audioUrl =
                        data.audio_url ||
                        data.url ||
                        data.audio;


                    if (!audioUrl) {

                        throw new Error(
                            "Audio was not returned."
                        );

                    }


                    storyAudio.src =
                        `${audioUrl}${audioUrl.includes("?") ? "&" : "?"}t=${Date.now()}`;


                    audioPanel.hidden =
                        false;


                    storyAudio.load();


                    try {

                        await storyAudio.play();

                    }
                    catch {

                        setStatus(
                            audioStatus,
                            "Audio ready. Press play."
                        );

                    }


                    setStatus(
                        audioStatus,
                        "Narration ready."
                    );

                }
                catch (error) {

                    console.error(
                        "TTS error:",
                        error
                    );


                    setStatus(
                        audioStatus,
                        error.message ||
                        "Narration failed.",
                        true
                    );

                }
                finally {

                    setLoading(
                        listenBtn,
                        false,
                        "LISTEN"
                    );

                }

            }
        );

    }


    // =====================================================
    // ASK AI
    // =====================================================

    if (askButton) {

        askButton.addEventListener(
            "click",
            async () => {

                const question =
                    questionInput?.value.trim();


                if (!question) {

                    setStatus(
                        aiStatus,
                        "Please ask a question."
                    );

                    questionInput?.focus();

                    return;

                }


                setLoading(
                    askButton,
                    true,
                    "ASK THE STORY →"
                );


                answerBox.hidden =
                    false;


                answerBox.textContent =
                    "Thinking...";


                setStatus(
                    aiStatus,
                    "Aryaverse AI is reading the story..."
                );


                try {

                    const response =
                        await fetch(
                            `/api/story/${storyId}/ask`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    question
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "AI request failed."
                        );

                    }


                    answerBox.textContent =
                        data.answer ||
                        data.text ||
                        data.response ||
                        "The story does not provide that information.";


                    setStatus(
                        aiStatus,
                        "Aryaverse Story AI"
                    );


                }
                catch (error) {

                    console.error(
                        "AI error:",
                        error
                    );


                    answerBox.textContent =
                        error.message;


                    setStatus(
                        aiStatus,
                        "AI unavailable.",
                        true
                    );

                }
                finally {

                    setLoading(
                        askButton,
                        false,
                        "ASK THE STORY →"
                    );

                }

            }
        );

    }


    // =====================================================
    // LOAD COMMENTS
    // =====================================================

    async function loadComments() {

        if (!commentsContainer) {
            return;
        }


        try {

            const response =
                await fetch(
                    `/api/story/${storyId}/comments`,
                    {
                        cache: "no-store"
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Comments unavailable."
                );

            }


            const comments =
                Array.isArray(data)
                    ? data
                    : (
                        data.comments ||
                        []
                    );


            if (!comments.length) {

                commentsContainer.innerHTML = `
                    <p class="empty-comments">
                        Be the first to share a thought.
                    </p>
                `;

                return;

            }


            commentsContainer.innerHTML =
                comments.map(
                    comment => `

                        <article class="comment">

                            <div class="comment-top">

                                <span class="comment-name">
                                    ${escapeHTML(
                                        comment.user_name ||
                                        comment.username ||
                                        "Visitor"
                                    )}
                                </span>

                                <span class="comment-date">
                                    ${escapeHTML(
                                        comment.created_at ||
                                        ""
                                    )}
                                </span>

                            </div>

                            <div class="comment-body">

                                ${escapeHTML(
                                    comment.comment ||
                                    ""
                                )}

                            </div>

                        </article>

                    `
                ).join("");


        }
        catch (error) {

            console.error(
                "Comments:",
                error
            );


            commentsContainer.innerHTML = `
                <p class="empty-comments">
                    Comments are unavailable.
                </p>
            `;

        }

    }


    // =====================================================
    // ADD COMMENT
    // =====================================================

    if (commentForm) {

        commentForm.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                const name =
                    commentName.value.trim();


                const comment =
                    commentText.value.trim();


                if (!name || !comment) {

                    setStatus(
                        commentStatus,
                        "Enter your name and comment."
                    );

                    return;

                }


                setStatus(
                    commentStatus,
                    "Publishing..."
                );


                try {

                    const response =
                        await fetch(
                            `/api/story/${storyId}/comments`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    user_name:
                                        name,

                                    comment:
                                        comment
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Comment failed."
                        );

                    }


                    commentText.value =
                        "";


                    setStatus(
                        commentStatus,
                        "Comment shared."
                    );


                    await loadComments();


                }
                catch (error) {

                    console.error(
                        error
                    );


                    setStatus(
                        commentStatus,
                        error.message,
                        true
                    );

                }

            }
        );

    }


    // =====================================================
    // LIKE
    // =====================================================

    if (likeBtn) {

        likeBtn.addEventListener(
            "click",
            async () => {

                try {

                    const name =
                        commentName?.value.trim() ||
                        localStorage.getItem(
                            "aryaverse_user"
                        ) ||
                        "Anonymous";


                    const response =
                        await fetch(
                            `/api/story/${storyId}/like`,
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    user_name:
                                        name
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            "Like failed."
                        );

                    }


                    likeBtn.classList.toggle(
                        "liked",
                        Boolean(data.liked)
                    );


                    likeBtn.textContent =
                        data.liked
                            ? "♥ STORY LIKED"
                            : "♡ LIKE STORY";


                    if (
                        typeof data.count !==
                        "undefined"
                    ) {

                        likeStatus.textContent =
                            `${data.count} likes`;

                    }

                }
                catch (error) {

                    console.error(
                        error
                    );

                    likeStatus.textContent =
                        error.message;

                }

            }
        );

    }


    // =====================================================
    // START COMMENTS
    // =====================================================

    loadComments();


    console.log(
        "Aryaverse story interface ready."
    );

});