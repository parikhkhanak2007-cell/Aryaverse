document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    // =====================================================
    // STATE PAGE
    // =====================================================

    const stateHeroImage =
        document.getElementById(
            "stateHeroImage"
        );


    /*
     * Keep the state page lightweight.
     *
     * Flask already renders the state
     * and Kutch region directly from
     * the database.
     */


    // =====================================================
    // IMAGE FALLBACK
    // =====================================================

    if (stateHeroImage) {

        stateHeroImage.addEventListener(
            "error",
            () => {

                /*
                 * Gujarat has a dedicated image.
                 * Use it if the database path
                 * is unavailable.
                 */

                if (
                    !stateHeroImage.src.includes(
                        "gujarat.png"
                    )
                ) {

                    stateHeroImage.src =
                        "/images/gujarat.png";

                }

            }
        );

    }


    // =====================================================
    // KUTCH CARD
    // =====================================================

    const regionCard =
        document.querySelector(
            ".region-card"
        );


    if (regionCard) {

        regionCard.addEventListener(
            "mouseenter",
            () => {

                regionCard.classList.add(
                    "active"
                );

            }
        );


        regionCard.addEventListener(
            "mouseleave",
            () => {

                regionCard.classList.remove(
                    "active"
                );

            }
        );

    }


    console.log(
        "Aryaverse state page ready."
    );

});