document.addEventListener("DOMContentLoaded", () => {

    // Get all states/UTs from the actual India SVG
    const paths = [
        ...document.querySelectorAll(
            "#indiaMap path[data-state]"
        )
    ];

    const title =
        document.getElementById("mapStateTitle");

    const status =
        document.getElementById("mapStatus");


    // State names
    const names = {
        "jammu-kashmir": "Jammu & Kashmir",
        "leh-ladakh": "Ladakh",

        "gujarat": "Gujarat",
        "rajasthan": "Rajasthan",
        "maharashtra": "Maharashtra",
        "madhya-pradesh": "Madhya Pradesh",

        "kerala": "Kerala",
        "tamil-nadu": "Tamil Nadu",
        "telangana": "Telangana",

        "punjab": "Punjab",
        "delhi": "Delhi",
        "haryana": "Haryana",

        "west-bengal": "West Bengal",
        "uttarakhand": "Uttarakhand",
        "uttar-pradesh": "Uttar Pradesh",

        "tripura": "Tripura",
        "sikkim": "Sikkim",
        "puducherry": "Puducherry",

        "odisha": "Odisha",
        "nagaland": "Nagaland",
        "mizoram": "Mizoram",
        "manipur": "Manipur",
        "meghalaya": "Meghalaya",

        "karnataka": "Karnataka",
        "jharkhand": "Jharkhand",
        "himachal-pradesh": "Himachal Pradesh",

        "goa": "Goa",

        "dadra-and-nagar-haveli":
            "Dadra & Nagar Haveli",

        "daman-and-diu":
            "Daman & Diu",

        "chhattisgarh":
            "Chhattisgarh",

        "chandigrah":
            "Chandigarh",

        "bihar":
            "Bihar",

        "assam":
            "Assam",

        "arunachal-pradesh":
            "Arunachal Pradesh",

        "andhra-pradesh":
            "Andhra Pradesh",

        "andaman-nicobar-islands":
            "Andaman & Nicobar Islands"
    };


    // Get readable state name
    function stateName(path) {

        const slug =
            path.dataset.state || "";

        return (
            names[slug] ||
            slug
                .replace(/-/g, " ")
                .replace(
                    /\b\w/g,
                    character =>
                        character.toUpperCase()
                )
        );
    }


    // Remove highlight from every state
    function clearActive() {

        paths.forEach(path => {

            path.classList.remove(
                "active-state"
            );

        });

    }


    // Add interactions to every state
    paths.forEach(path => {

        const slug =
            path.dataset.state;

        const name =
            stateName(path);


        // Accessibility label
        path.setAttribute(
            "aria-label",
            `Explore ${name}`
        );


        // Browser tooltip
        path.setAttribute(
            "title",
            name
        );


        // =============================
        // HOVER
        // =============================

        path.addEventListener(
            "mouseenter",
            () => {

                clearActive();

                path.classList.add(
                    "active-state"
                );

                if (title) {
                    title.textContent =
                        name;
                }

                if (status) {
                    status.textContent =
                        "Click to explore";
                }

            }
        );


        // =============================
        // MOUSE LEAVE
        // =============================

        path.addEventListener(
            "mouseleave",
            () => {

                clearActive();

                if (title) {
                    title.textContent =
                        "Explore India";
                }

                if (status) {
                    status.textContent =
                        "Hover over a state";
                }

            }
        );


        // =============================
        // CLICK
        // =============================

        path.addEventListener(
            "click",
            () => {

                if (!slug) {
                    return;
                }

                window.location.href =
                    `/state/${encodeURIComponent(slug)}`;

            }
        );

    });


    // =============================
    // INITIAL MESSAGE
    // =============================

    if (title) {
        title.textContent =
            "Explore India";
    }

    if (status) {
        status.textContent =
            "Hover over a state";
    }


    console.log(
        `ARYAVERSE map ready — ${paths.length} states/UTs loaded.`
    );

});