function uploadResume() {
    let fileInput = document.getElementById("file").files[0];

    let formData = new FormData();
    formData.append("file", fileInput);

    fetch("http://127.0.0.1:8000/api/resumes/upload/", {
        method: "POST",
        headers: {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2NTA2MjExLCJpYXQiOjE3NzY0MTk4MTEsImp0aSI6ImRmYmE3YmQ2YWI5ZTQyMThhZjU3YmQ0MmIzZGRlMDdlIiwidXNlcl9pZCI6IjYifQ.D5XZYi7U86v396tgKSRyUlF0RdokFFGOEd91BMo1-C8"
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

    fetch("http://127.0.0.1:8000/api/jobs/all-profiles/", {
        headers: {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc2NTA3MDExLCJpYXQiOjE3NzY0MjA2MTEsImp0aSI6IjM5NTE0ZmQwYTg5ODQxNTlhNTUyN2VmMDQ1NmZiZjZhIiwidXNlcl9pZCI6IjgifQ.Pmlz5hGZvhdLBhcJjlhfROFt3DhT0zcv8FtVkXf0MJo"
        }
    })
    .then(data => {

        if (!Array.isArray(data)) {
            document.getElementById("output").innerText = JSON.stringify(data, null, 2);
            return;
        }
    
        let output = "";
    
        data.forEach(item => {
    
            let colorClass = item.decision.includes("Shortlisted") ? "green" : "red";
    
            output += `
            <div class="result-card">
                <b>Resume ID:</b> ${item.resume_id} <br>
                <b>Score:</b> ${item.score}% <br>
                <b>Level:</b> ${item.level} <br>
                <b>Decision:</b> <span class="${colorClass}">${item.decision}</span>
            </div>
            `;
        });
    
        document.getElementById("output").innerHTML = output;
    })
        document.getElementById("output").innerText = "Error: " + error;
    });
}