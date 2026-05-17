function addExperience() {

    const formData = new URLSearchParams({

        company_name:
        document.getElementById("company").value,

        role:
        document.getElementById("role").value,

        difficulty:
        document.getElementById("difficulty").value,

        round_type:
        document.getElementById("round").value,

        experience_text:
        document.getElementById("text").value
    });

    fetch("/add_experience", {

        method: "POST",

        headers: {

            "Content-Type":
            "application/x-www-form-urlencoded",

            "Authorization":
            `Bearer ${localStorage.getItem("token")}`
        },

        body: formData
    })

    .then(res => res.text())

    .then(data => {

        alert(data);

        // CLEAR INPUTS

        document.getElementById(
            "company"
        ).value = "";

        document.getElementById(
            "role"
        ).value = "";

        document.getElementById(
            "difficulty"
        ).value = "";

        document.getElementById(
            "round"
        ).value = "";

        document.getElementById(
            "text"
        ).value = "";

        getExperiences();
    })

    .catch(error =>
        console.error(
            "Error adding experience:",
            error
        )
    );
}

// GET EXPERIENCES

function getExperiences() {

    let company =
        document.getElementById(
            "filterCompany"
        ).value;

    let url = "/experiences";

    if(company) {

        url +=
        "?company=" +
        encodeURIComponent(company);
    }

    fetch(url)

    .then(res => res.json())

    .then(data => {

        let output = "";

        if(data.experiences.length === 0) {

            output =
            "<p>No experiences found.</p>";
        }

        else {

            // SORT BY UPVOTES

            data.experiences.sort(
                (a, b) =>
                b.upvotes - a.upvotes
            );

            data.experiences.forEach(exp => {

                output += `

                    <div class="card">

                        <h2>
                            ${exp.company_name}
                        </h2>

                        <p>
                            👤 Posted by:
                            <b>
                                ${exp.username}
                            </b>
                        </p>

                        <p>
                            🕒
                            ${exp.created_at}
                        </p>

                        <p>
                            <strong>
                                ${exp.role}
                            </strong>

                            |

                            ${exp.difficulty}

                        </p>

                        <p>
                            <em>
                                ${exp.round_type}
                            </em>
                        </p>

                        <p>
                            ${exp.experience_text}
                        </p>

                        <p>
                            ❤️ Upvotes:
                            <b>
                                ${exp.upvotes || 0}
                            </b>
                        </p>

                        <div class="actions">

                            <button onclick="upvote(${exp.id})">

                                ❤️ Like

                            </button>

                            <button onclick="editExperience(
                                ${exp.id},
                                '${exp.company_name}',
                                '${exp.role}',
                                '${exp.round_type}',
                                '${exp.difficulty}',
                                \`${exp.experience_text}\`
                            )">

                                ✏️ Edit

                            </button>

                            <button onclick="deleteExperience(${exp.id})">

                                🗑 Delete

                            </button>

                        </div>

                    </div>
                `;
            });
        }

        document.getElementById(
            "output"
        ).innerHTML = output;
    })

    .catch(error =>
        console.error(
            "Error fetching experiences:",
            error
        )
    );
}

// OPEN AI PROJECT

function openAIProject() {

    window.open(
        "http://127.0.0.1:5001/",
        "_blank"
    );
}

// DELETE EXPERIENCE

async function deleteExperience(id) {

    await fetch(
        `/delete_experience/${id}`,
        {
            method: "DELETE",

            headers: {

                "Authorization":
                `Bearer ${localStorage.getItem("token")}`
            }
        }
    );

    getExperiences();
}

// UPVOTE

async function upvote(id) {

    await fetch(
        `/upvote/${id}`,
        {
            method: "POST",

            headers: {

                "Authorization":
                `Bearer ${localStorage.getItem("token")}`
            }
        }
    );

    getExperiences();
}

// EDIT EXPERIENCE

function editExperience(
    id,
    company,
    role,
    round,
    difficulty,
    text
) {

    document.getElementById(
        "company"
    ).value = company;

    document.getElementById(
        "role"
    ).value = role;

    document.getElementById(
        "round"
    ).value = round;

    document.getElementById(
        "difficulty"
    ).value = difficulty;

    document.getElementById(
        "text"
    ).value = text;
}

// LOAD ON START

window.onload = getExperiences;