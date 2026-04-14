function uploadResume() {
    let fileInput = document.getElementById("file").files[0];

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch("http://127.0.0.1:8000/api/resumes/upload/", {
        method: "POST",
        headers: {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2MTc5MTMxLCJpYXQiOjE3NzYwOTI3MzEsImp0aSI6IjYyOGIzM2IzMGI1NTQ0NWQ4OGIzZDY5MGE5NTI3Zjc5IiwidXNlcl9pZCI6IjEifQ.CPJ5wF8ml6JJrETpAWI2qGoaYSjTdINXSUt-1rT54Xo"
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        document.getElementById("output").innerText = "Error: " + error;
    });
}
function getResults() {
    document.getElementById("output").innerText = "Loading...";

    fetch("http://127.0.0.1:8000/api/jobs/all-profiles/")
    .then(res => res.json())
    .then(data => {
        let output = "";

        data.forEach(item => {
            output += `
Resume ID: ${item.resume_id}
Score: ${item.score}%
Level: ${item.level}

Decision: <span style="color:${
    item.decision.includes("Rejected") ? "red" :
    item.decision.includes("Review") ? "orange" : "green"
}">
${item.decision}
</span>

Review Note: ${item.review_note}
Message: ${item.message}

----------------------
`;
        });

        document.getElementById("output").innerHTML = output;
    })
    .catch(error => {
        document.getElementById("output").innerText = "Error: " + error;
    });
}