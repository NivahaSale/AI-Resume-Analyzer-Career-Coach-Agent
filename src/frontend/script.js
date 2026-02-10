if (!localStorage.getItem("token")) {
    window.location.href = "login.html";
}

async function analyzeResume() {
    const fileInput = document.getElementById("resume");
    const results = document.getElementById("results");
    const score = document.getElementById("score");
    const skills = document.getElementById("skills");
    const tips = document.getElementById("tips");

    if (!fileInput.files.length) {
        alert("Please upload a resume (PDF)");
        return;
    }

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);

    results.classList.remove("hidden");
    score.innerText = "Analyzing...";
    skills.innerHTML = "";
    tips.innerHTML = "";

    try {
        const response = await fetch("http://localhost:8000/api/analyze-resume", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        score.innerText = data.ats_score || 0;

        (data.skills_found || []).forEach(skill => {
            skills.innerHTML += `<li>${skill}</li>`;
        });

        (data.recommendations || []).forEach(tip => {
            tips.innerHTML += `<li>${tip}</li>`;
        });

    } catch (err) {
        alert("Backend not reachable");
    }
}

