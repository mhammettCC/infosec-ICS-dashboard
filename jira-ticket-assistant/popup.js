document.addEventListener("DOMContentLoaded", () => {
  const templateSelect = document.getElementById("template");
  const statusEl = document.getElementById("status");
  const templateDetails = document.getElementById("templateDetails");
  let currentTemplates = {};

  // Load templates from local storage and populate dropdown
  chrome.storage.local.get(["templates"], (data) => {
    const templates = data.templates || {};
    currentTemplates = templates;

    templateSelect.innerHTML = '<option value="">-- No Template --</option>';
    Object.entries(templates).forEach(([key]) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = key;
      templateSelect.appendChild(option);
    });
  });

  // Show template details on selection change
  templateSelect.addEventListener("change", () => {
    const key = templateSelect.value;
    if (!key) {
      templateDetails.innerHTML = "";
      return;
    }

    const template = currentTemplates[key];
    if (!template) {
      templateDetails.innerHTML = "Template not found.";
      return;
    }

    const descriptionHtml = template.description
      .map(line => `<li>${line}</li>`)
      .join("");

    templateDetails.innerHTML = `
      <strong>Summary:</strong> ${template.summary}<br />
      <strong>Labels:</strong> ${template.labels.join(", ")}<br />
      <strong>Description:</strong>
      <ul>${descriptionHtml}</ul>
    `;
  });

  // Create ticket on button click
    document.getElementById("create").addEventListener("click", async () => {
      statusEl.textContent = "Creating ticket...";

      const summaryInput = document.getElementById("summary").value.trim();
      const templateKey = templateSelect.value;

      // ✅ FIXED: Get quarter and iteration selections from your actual HTML
      const selectedQuarters = Array.from(document.querySelectorAll("#quarters input[type='checkbox']:checked"))
        .map(el => el.value);
      const selectedItems = Array.from(document.querySelectorAll("#impacts input[type='checkbox']:checked"))
        .map(el => el.value);

      const currentYear = new Date().getFullYear();
      let formattedTag = `[${currentYear}`;
        if (selectedQuarters.length) {
          formattedTag += `.${selectedQuarters.join(",")}`;
        }
        if (selectedItems.length) {
          formattedTag += `.${selectedItems.join(",")}`;
        }
        formattedTag += `]`;

      if (!summaryInput) {
        statusEl.textContent = "Please enter a summary.";
        return;
      }

    chrome.storage.local.get(["domain", "email", "project", "templates"], async (settings) => {
      if (!settings.domain || !settings.email || !settings.project) {
        statusEl.textContent = "Please configure settings first.";
        return;
      }

      const templates = settings.templates || {};
      let finalSummary = summaryInput;
      let descriptionText = summaryInput
      let labels = [];

     const yearLabel = `${currentYear}`;
     const quarterLabels = selectedQuarters.map(q => `${q}`);
     const impactLabels = selectedItems.map(i => `${i}`);

    // Include template labels if any
    if (templateKey && templates[templateKey]) {
      const template = templates[templateKey];
      finalSummary = `${formattedTag} ${template.summary} ${summaryInput}`;
      labels = [...(template.labels || [])];
      descriptionText = template.description.join('\n');
    } else {
      finalSummary = `${formattedTag} ${summaryInput}`;
    }

    // Append year, quarter, and impact labels
    labels = [...new Set([...labels, yearLabel, ...quarterLabels, ...impactLabels])];

      const isStory = document.getElementById("isStory").checked;
      const issueTypeName = isStory ? "Story" : "Task";
      const selectedPriority = document.getElementById("priority").value;

      const issueData = {
        fields: {
          project: { key: settings.project },
          summary: finalSummary,
          description: descriptionText,
          issuetype: { name: issueTypeName },
          labels,
          priority: { name: selectedPriority },
          assignee: { name: "" }
        }
      };

      try {
        const response = await fetch(`https://${settings.domain}/rest/api/2/issue`, {
          method: "POST",
          headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(issueData)
        });

        if (response.ok) {
          const result = await response.json();
          const ticketKey = result.key;
          const ticketUrl = `https://${settings.domain}/browse/${ticketKey}`;
          statusEl.innerHTML = `<a href="${ticketUrl}" target="_blank">${ticketKey}</a> created successfully!`;
          chrome.storage.local.set({ lastError: "" });
        } else {
          let errorText = `HTTP Error ${response.status}`;
          let fullError = "";
          try {
            const errorBody = await response.json();
            fullError = JSON.stringify(errorBody, null, 2);
            if (errorBody.errorMessages?.length) {
              errorText += `: ${errorBody.errorMessages.join(", ")}`;
            } else if (errorBody.message) {
              errorText += `: ${errorBody.message}`;
            } else {
              errorText += `: ${fullError}`;
            }
          } catch {
            fullError = await response.text();
            errorText += `: ${fullError}`;
          }
          statusEl.textContent = errorText;
          chrome.storage.local.set({ lastError: fullError || errorText });
        }
      } catch (err) {
        const fetchError = `Fetch error: ${err.message}`;
        statusEl.textContent = fetchError;
        chrome.storage.local.set({ lastError: fetchError });
      }
    });
  });

  // Open settings/options page
  document.getElementById("settings").addEventListener("click", () => {
    if (chrome.runtime.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      window.open(chrome.runtime.getURL("options.html"));
    }
  });
});
