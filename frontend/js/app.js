const audioFile =
    document.getElementById("audioFile");

const dropZone =
    document.getElementById("dropZone");

const selectedFile =
    document.getElementById("selectedFile");

const generateButton =
    document.getElementById("generateButton");

const processingSection =
    document.getElementById("processingSection");

const resultSection =
    document.getElementById("resultSection");

const newMeetingButton =
    document.getElementById("newMeetingButton");


// ==========================================
// FILE SELECTION
// ==========================================

dropZone.addEventListener(
    "click",
    () => {

        audioFile.click();

    }
);


audioFile.addEventListener(
    "change",
    () => {

        if (audioFile.files.length > 0) {

            showSelectedFile(
                audioFile.files[0]
            );

        }

    }
);


// ==========================================
// DRAG AND DROP
// ==========================================

dropZone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        dropZone.classList.add(
            "dragover"
        );

    }
);


dropZone.addEventListener(
    "dragleave",
    () => {

        dropZone.classList.remove(
            "dragover"
        );

    }
);


dropZone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        dropZone.classList.remove(
            "dragover"
        );

        const files =
            event.dataTransfer.files;

        if (files.length > 0) {

            audioFile.files = files;

            showSelectedFile(
                files[0]
            );

        }

    }
);


// ==========================================
// SHOW SELECTED FILE
// ==========================================

function showSelectedFile(file) {

    selectedFile.textContent =
        `✓ ${file.name}`;

    generateButton.disabled = false;

}


// ==========================================
// GENERATE MOM
// ==========================================

generateButton.addEventListener(
    "click",
    async () => {

        if (!audioFile.files.length) {

            return;

        }

        // Hide upload
        document
            .querySelector(".upload-section")
            .classList.add("hidden");


        // Show processing
        processingSection.classList.remove(
            "hidden"
        );


        // Simulate processing
        await simulateProcessing();


        // Show result
        processingSection.classList.add(
            "hidden"
        );

        resultSection.classList.remove(
            "hidden"
        );


        // Temporary dummy response
        displayMoM(
            getDummyMoM()
        );

    }
);


// ==========================================
// SIMULATE PROCESSING
// ==========================================

async function simulateProcessing() {

    const processingText =
        document.getElementById(
            "processingText"
        );


    processingText.textContent =
        "Transcribing meeting...";

    await wait(1200);


    processingText.textContent =
        "Identifying speakers...";

    document
        .getElementById(
            "stepDiarization"
        )
        .classList.add("active");

    await wait(1200);


    processingText.textContent =
        "Analyzing conversation with AI...";

    document
        .getElementById(
            "stepAnalysis"
        )
        .classList.add("active");

    await wait(1200);


    processingText.textContent =
        "Generating Minutes of Meeting...";

    document
        .getElementById(
            "stepGeneration"
        )
        .classList.add("active");

    await wait(1200);

}


function wait(milliseconds) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
            )
    );

}


// ==========================================
// DISPLAY MOM
// ==========================================

function displayMoM(mom) {

    document.getElementById(
        "meetingTitle"
    ).textContent =
        mom.title;


    document.getElementById(
        "summary"
    ).textContent =
        mom.summary;


    // --------------------------------------
    // Discussion points
    // --------------------------------------

    const discussionContainer =
        document.getElementById(
            "discussionPoints"
        );

    discussionContainer.innerHTML = "";


    mom.key_discussion_points.forEach(
        (point, index) => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "discussion-item";

            div.innerHTML = `
                <span class="discussion-number">
                    ${index + 1}.
                </span>

                ${escapeHTML(point)}
            `;

            discussionContainer.appendChild(
                div
            );

        }
    );


    // --------------------------------------
    // Decisions
    // --------------------------------------

    const decisionsContainer =
        document.getElementById(
            "decisions"
        );

    decisionsContainer.innerHTML = "";


    mom.decisions.forEach(
        decision => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "decision-item";

            div.innerHTML = `

                <div>
                    ${escapeHTML(
                        decision.decision
                    )}
                </div>

                <div class="decision-owner">
                    👤 ${escapeHTML(
                        decision.made_by
                    )}
                </div>

            `;

            decisionsContainer.appendChild(
                div
            );

        }
    );


    // --------------------------------------
    // Action items
    // --------------------------------------

    const actionContainer =
        document.getElementById(
            "actionItems"
        );

    actionContainer.innerHTML = "";


    mom.action_items.forEach(
        item => {

            const row =
                document.createElement(
                    "tr"
                );

            const deadline =
                item.deadline
                    ? escapeHTML(
                        item.deadline
                    )
                    : `<span class="deadline-none">
                        —
                       </span>`;


            row.innerHTML = `

                <td>
                    ${escapeHTML(
                        item.task
                    )}
                </td>

                <td>
                    <span class="owner-badge">
                        ${escapeHTML(
                            item.owner
                        )}
                    </span>
                </td>

                <td>
                    ${deadline}
                </td>

            `;

            actionContainer.appendChild(
                row
            );

        }
    );


    // --------------------------------------
    // Open questions
    // --------------------------------------

    const questionsContainer =
        document.getElementById(
            "openQuestions"
        );

    questionsContainer.innerHTML = "";


    mom.open_questions.forEach(
        question => {

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "question-item";

            div.textContent =
                question;

            questionsContainer.appendChild(
                div
            );

        }
    );

}


// ==========================================
// NEW MEETING
// ==========================================

newMeetingButton.addEventListener(
    "click",
    () => {

        location.reload();

    }
);


// ==========================================
// TEMPORARY DUMMY DATA
// ==========================================

function getDummyMoM() {

    return {

        title:
            "Meeting on Data Collection Volunteers, Incentives, and Disk Resource Management",

        summary:
            "The team discussed strategies to bring volunteers into their room for meeting recordings, prioritizing participants outside of engineering and linguistics. Incentive ideas included free lunch and providing recordings/transcripts post-screening. SPEAKER_00 agreed to contact potential volunteers from Haas Business School. Additionally, SPEAKER_00 gave an update on archiving broadcast news P files to free up 10 GB of disk space for future recordings.",

        key_discussion_points: [

            "Prioritizing bringing volunteers to the on-site recording room rather than transporting equipment.",

            "Targeting a broader demographic of participants beyond engineers and linguists, using free lunch as an incentive.",

            "Providing participants with a CD/transcript of their meeting only after the transcript screening phase to avoid privacy and legal issues.",

            "Managing disk storage resources by archiving and cloning broadcast news P files to free up 10 GB of space for recording five more meetings."

        ],

        decisions: [

            {
                decision:
                    "Focus on bringing volunteers to the local room for meeting recordings as the primary priority.",

                made_by:
                    "SPEAKER_01"
            },

            {
                decision:
                    "Pursue volunteer contacts from the Haas Business School.",

                made_by:
                    "SPEAKER_02"
            }

        ],

        action_items: [

            {
                task:
                    "Send an email inquiry to contacts at Haas Business School regarding volunteering and mention the free lunch.",

                owner:
                    "SPEAKER_00",

                deadline:
                    null
            },

            {
                task:
                    "Complete archiving and cloning of broadcast news P files and delete the original files to free up 10 GB of disk space.",

                owner:
                    "SPEAKER_00",

                deadline:
                    null
            }

        ],

        open_questions: [

            "Whether the volunteers from Haas Business School will still be willing to participate given that they decided not to go into speech."

        ]

    };

}


// ==========================================
// BASIC HTML SAFETY
// ==========================================

function escapeHTML(value) {

    if (value === null ||
        value === undefined) {

        return "";

    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}