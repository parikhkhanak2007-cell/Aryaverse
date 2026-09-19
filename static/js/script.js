/* =========================================================
   ARYAVERSE
   MAIN WEBSITE JAVASCRIPT
========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    () => {


        /* =================================================
           ELEMENTS
        ================================================== */

        const openingScreen =
            document.getElementById(
                "openingScreen"
            );


        const enterScreen =
            document.getElementById(
                "enterScreen"
            );


        const openingVideo =
            document.getElementById(
                "openingVideo"
            );


        const enterButton =
            document.getElementById(
                "enterButton"
            );


        const mainSite =
            document.getElementById(
                "mainSite"
            );


        let entering = false;



        /* =================================================
           INITIAL STATE
        ================================================== */

        document.body.classList.add(
            "opening-active"
        );


        /*
         * Video is deliberately paused
         * until ENTER is clicked.
         */

        openingVideo.pause();

        openingVideo.currentTime = 0;



        /* =================================================
           ENTER
           
           ENTER CLICK
               ↓
           Button disappears
               ↓
           Video starts
        ================================================== */

        enterButton.addEventListener(
            "click",
            async () => {


                if (entering) {
                    return;
                }


                entering = true;


                /*
                 * Disable the button immediately.
                 */

                enterButton.disabled =
                    true;


                /*
                 * Hide the complete
                 * ENTER overlay immediately.
                 *
                 * This means there is
                 * NO ENTER button while
                 * the cinematic video plays.
                 */

                enterScreen.classList.add(
                    "hidden"
                );


                /*
                 * Make the video visible.
                 */

                openingScreen.classList.add(
                    "video-playing"
                );


                /*
                 * Always begin from
                 * the first frame.
                 */

                openingVideo.currentTime = 0;


                try {

                    await openingVideo.play();


                    console.log(
                        "ARYAVERSE opening video started."
                    );


                } catch (error) {

                    console.error(
                        "Could not start opening video:",
                        error
                    );


                    /*
                     * If the browser refuses
                     * playback, don't leave
                     * the visitor stuck.
                     */

                    setTimeout(
                        showHome,
                        1000
                    );

                }

            }
        );



        /* =================================================
           VIDEO FINISHED
        ================================================== */

        openingVideo.addEventListener(
            "ended",
            () => {


                console.log(
                    "ARYAVERSE opening video finished."
                );


                /*
                 * Small cinematic pause
                 * before revealing home.
                 */

                setTimeout(
                    showHome,
                    500
                );

            }
        );



        /* =================================================
           VIDEO ERROR
        ================================================== */

        openingVideo.addEventListener(
            "error",
            () => {


                console.error(
                    "ARYAVERSE opening video error."
                );


                /*
                 * Fallback so the user
                 * can still enter the site.
                 */

                setTimeout(
                    showHome,
                    700
                );

            }
        );



        /* =================================================
           SHOW HOME PAGE
        ================================================== */

        function showHome() {


            /*
             * Hide opening.
             */

            openingScreen.classList.add(
                "hidden"
            );


            /*
             * Reveal website.
             */

            mainSite.classList.add(
                "visible"
            );


            /*
             * Allow scrolling.
             */

            document.body.classList.remove(
                "opening-active"
            );


            /*
             * Start homepage at top.
             */

            window.scrollTo(
                0,
                0
            );


            /*
             * Stop video after
             * transition has completed.
             */

            setTimeout(
                () => {

                    openingVideo.pause();

                },
                1500
            );

        }



        /* =================================================
           NAVBAR ACTIVE STATE
        ================================================== */

        const sections =
            document.querySelectorAll(
                "main section[id]"
            );


        const navLinks =
            document.querySelectorAll(
                ".nav-links a"
            );


        if (
            sections.length &&
            navLinks.length
        ) {


            const observer =
                new IntersectionObserver(
                    entries => {


                        entries.forEach(
                            entry => {


                                if (
                                    !entry.isIntersecting
                                ) {

                                    return;

                                }


                                const sectionId =
                                    entry.target.id;


                                navLinks.forEach(
                                    link => {

                                        link.classList.remove(
                                            "active"
                                        );


                                        const href =
                                            link.getAttribute(
                                                "href"
                                            );


                                        if (
                                            href ===
                                            `#${sectionId}`
                                        ) {

                                            link.classList.add(
                                                "active"
                                            );

                                        }

                                    }
                                );

                            }
                        );

                    },
                    {
                        threshold:
                            0.35
                    }
                );


            sections.forEach(
                section => {

                    observer.observe(
                        section
                    );

                }
            );

        }



        /* =================================================
           SMOOTH INTERNAL LINKS
        ================================================== */

        const internalLinks =
            document.querySelectorAll(
                'a[href^="#"]'
            );


        internalLinks.forEach(
            link => {


                link.addEventListener(
                    "click",
                    event => {


                        const targetId =
                            link.getAttribute(
                                "href"
                            );


                        if (
                            !targetId ||
                            targetId === "#"
                        ) {

                            return;

                        }


                        const target =
                            document.querySelector(
                                targetId
                            );


                        if (!target) {

                            return;

                        }


                        event.preventDefault();


                        target.scrollIntoView({
                            behavior:
                                "smooth",

                            block:
                                "start"
                        });


                    }
                );

            }
        );



        /* =================================================
           IMAGE ERROR CHECK
        ================================================== */

        document
            .querySelectorAll("img")
            .forEach(
                image => {


                    image.addEventListener(
                        "error",
                        () => {

                            console.error(
                                "ARYAVERSE IMAGE NOT FOUND:",
                                image.src
                            );

                        }
                    );

                }
            );



        /* =================================================
           DEBUG
        ================================================== */

        console.log(
            "ARYAVERSE HOME READY"
        );

        console.log(
            "Opening video:",
            openingVideo
        );

        console.log(
            "Enter button:",
            enterButton
        );

        console.log(
            "Navbar:",
            document.querySelector(
                ".navbar"
            )
        );

    }
);