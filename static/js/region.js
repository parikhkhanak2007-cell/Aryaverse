document.addEventListener("DOMContentLoaded", () => {

    const experienceCards =
        document.querySelectorAll(
            ".experience-card"
        );


    /*
     * =====================================
     * EXPERIENCE CARD INTERACTIONS
     * =====================================
     */

    experienceCards.forEach(card => {

        card.addEventListener(
            "mouseenter",
            () => {

                card.classList.add(
                    "active"
                );

            }
        );


        card.addEventListener(
            "mouseleave",
            () => {

                card.classList.remove(
                    "active"
                );

            }
        );

    });


    /*
     * =====================================
     * IMAGE FALLBACK
     * =====================================
     */

    const images =
        document.querySelectorAll(
            "img"
        );


    images.forEach(image => {

        image.addEventListener(
            "error",
            () => {

                /*
                 * Prevent broken images.
                 * Use India image only as a fallback.
                 */

                if (
                    !image.dataset.fallback
                ) {

                    image.dataset.fallback =
                        "true";

                    image.src =
                        "/images/india.png";

                }

            }
        );

    });


    /*
     * =====================================
     * FOLK STORY CARD
     * =====================================
     *
     * Clicking the Folk Stories
     * experience scrolls to the
     * database stories.
     */

    const folkCard =
        document.querySelector(
            '[data-experience="stories"]'
        );


    const storiesSection =
        document.getElementById(
            "folk-stories"
        );


    if (
        folkCard &&
        storiesSection
    ) {

        folkCard.addEventListener(
            "click",
            () => {

                storiesSection.scrollIntoView({
                    behavior: "smooth"
                });

            }
        );

    }


    /*
     * =====================================
     * FOOD / FESTIVAL / TEXTILE
     * =====================================
     *
     * These currently behave as
     * immersive category cards.
     *
     * They can later be connected
     * to dedicated backend experiences.
     */

    const foodCard =
        document.querySelector(
            '[data-experience="food"]'
        );


    const festivalCard =
        document.querySelector(
            '[data-experience="festivals"]'
        );


    const textileCard =
        document.querySelector(
            '[data-experience="textiles"]'
        );


    function categoryMessage(card) {

        if (!card) {
            return;
        }


        card.addEventListener(
            "click",
            () => {

                const type =
                    card.dataset.experience;


                console.log(
                    `Aryaverse experience: ${type}`
                );

            }
        );

    }


    categoryMessage(foodCard);

    categoryMessage(festivalCard);

    categoryMessage(textileCard);


    console.log(
        "Aryaverse region page loaded."
    );

});