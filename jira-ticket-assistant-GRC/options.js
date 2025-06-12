document.addEventListener("DOMContentLoaded", () => {
  const domain = document.getElementById("domain");
  const email = document.getElementById("email");
  const project = document.getElementById("project");
  const status = document.getElementById("status");
  const templatesContainer = document.getElementById("templatesContainer");

  const newKeyInput = document.getElementById("newKey");
  const newSummaryInput = document.getElementById("newSummary");
  const newLabelsInput = document.getElementById("newLabels");
  const newDescriptionInput = document.getElementById("newDescription");

  const defaultTemplates = {
    "Template": {
      summary: "",
      labels: [""],
      description: [
        "*Estimated Story Point*: X",
        "",
        "*Actual Story Point*: X",
        "",
        "*Definition of Done*:"
      ]
    }
  };

  chrome.storage.local.get(
    ["domain", "email", "project", "templates", "lastError"],
    (data) => {
      domain.value = data.domain || "";
      email.value = data.email || "";
      project.value = data.project || "";

      if (!data.templates || Object.keys(data.templates).length === 0) {
        chrome.storage.local.set({ templates: defaultTemplates }, () => {
          renderTemplates(defaultTemplates);
        });
      } else {
        renderTemplates(data.templates);
      }
    }
  );

  document.getElementById("save").addEventListener("click", () => {
    chrome.storage.local.set(
      {
        domain: domain.value.trim(),
        email: email.value.trim(),
        project: project.value.trim()
      },
      () => {
        status.textContent = "Settings saved.";
        setTimeout(() => {
          status.textContent = "";
        }, 3000);
      }
    );
  });

  function renderTemplates(templates) {
    templatesContainer.innerHTML = "";
    Object.entries(templates).forEach(([key, template]) => {
      const div = document.createElement("div");
      div.className = "template-block";

      div.innerHTML = `
        <h4>${key}</h4>
        <strong>Summary:</strong> ${template.summary}<br />
        <strong>Labels:</strong> ${template.labels.join(", ")}<br />
        <strong>Description:</strong>
        <ul>${template.description.map(line => `<li>${line}</li>`).join("")}</ul>
        <div class="template-actions">
          <button data-key="${key}" class="editBtn">Edit</button>
          <button data-key="${key}" class="deleteBtn">Delete</button>
        </div>
      `;
      templatesContainer.appendChild(div);
    });

    document.querySelectorAll(".deleteBtn").forEach(btn => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-key");
        chrome.storage.local.get("templates", (data) => {
          const templates = data.templates || {};
          delete templates[key];
          chrome.storage.local.set({ templates }, () => renderTemplates(templates));
        });
      });
    });

    document.querySelectorAll(".editBtn").forEach(btn => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-key");
        chrome.storage.local.get("templates", (data) => {
          const template = data.templates[key];
          newKeyInput.value = key;
          newSummaryInput.value = template.summary;
          newLabelsInput.value = template.labels.join(", ");
          newDescriptionInput.value = template.description.join("\n");
        });
      });
    });
  }

  document.getElementById("addTemplate").addEventListener("click", () => {
    const key = newKeyInput.value.trim();
    const summary = newSummaryInput.value.trim();
    const labels = newLabelsInput.value.split(",").map(l => l.trim()).filter(Boolean);
    const description = newDescriptionInput.value.split("\n").map(line => line.trim()).filter(Boolean);

    if (!key || !summary || labels.length === 0 || description.length === 0) {
      alert("Please fill in all fields to add or update a template.");
      return;
    }

    chrome.storage.local.get("templates", (data) => {
      const templates = data.templates || {};
      templates[key] = { summary, labels, description };
      chrome.storage.local.set({ templates }, () => {
        renderTemplates(templates);
        newKeyInput.value = "";
        newSummaryInput.value = "";
        newLabelsInput.value = "";
        newDescriptionInput.value = "";
        status.textContent = `Template "${key}" saved.`;
        setTimeout(() => { status.textContent = ""; }, 3000);
      });
    });
  });
});
