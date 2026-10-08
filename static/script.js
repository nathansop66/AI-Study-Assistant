const askButton = document.getElementById("askButton");
const helpType = document.getElementById("helpType");
const studentInput = document.getElementById("studentInput");
const responseBox = document.getElementById("response");

askButton.addEventListener("click", async function () {

    console.log("ASK BUTTON CLICKED");

    const selectedHelpType = helpType.value;
    const studentQuestion = studentInput.value.trim();

    if (!studentQuestion) {
        responseBox.textContent = "Please enter a question or idea first.";
        return;
    }

    responseBox.textContent = "Thinking...";

    try {

        console.log("SENDING REQUEST TO PYTHON...");

        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                helpType: selectedHelpType,
                studentInput: studentQuestion
            })
        });

        console.log("PYTHON RESPONSE STATUS:", response.status);

        const data = await response.json();

        console.log("PYTHON RESPONSE:", data);

        responseBox.textContent =
            data.response || "The AI did not return a response.";

    } catch (error) {

        console.error("ERROR:", error);

        responseBox.textContent =
            "Something went wrong. Please try again.";
    }
});