// Browser client for chat and lead capture. It sends only form data to the API.
const messages = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("message");
const sendButton = document.getElementById("sendButton");
const leadDialog = document.getElementById("leadDialog");
const leadForm = document.getElementById("leadForm");
const leadStatus = document.getElementById("leadStatus");

// In production the frontend is served by FastAPI and uses the same origin.
// When opened with file:// or VS Code Live Server during local development,
// send API requests to the FastAPI server running on port 8000 instead.
const isLocalPreview = window.location.protocol === "file:" || (
  ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
  window.location.port !== "" && window.location.port !== "8000"
);
const apiBaseUrl = isLocalPreview ? "http://127.0.0.1:8000" : "";

function addMessage(text, role) {
  document.querySelector(".welcome-message")?.remove();
  const message = document.createElement("div");
  message.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") {
    renderAssistantAnswer(bubble, text);
  } else {
    bubble.textContent = text;
  }
  message.append(bubble);
  messages.append(message);
  messages.scrollTop = messages.scrollHeight;
}

function splitTableRow(line) {
  // Return safe cell text from a simple Markdown table row.
  return line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
}

function isTableDivider(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function addTextLine(container, line) {
  if (!line.trim()) return;
  const paragraph = document.createElement("p");
  // Keep model output safe: it is inserted as text, never HTML.
  paragraph.textContent = line.replace(/^\*\*(.+)\*\*$/, "$1");
  container.append(paragraph);
}

function renderAssistantAnswer(container, text) {
  // Render ordinary answer text and NIM's Markdown tables without unsafe HTML.
  const lines = text.split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const header = lines[index];
    const divider = lines[index + 1];
    if (header?.includes("|") && isTableDivider(divider || "")) {
      const wrapper = document.createElement("div");
      wrapper.className = "table-wrapper";
      const table = document.createElement("table");
      const tableHead = document.createElement("thead");
      const headingRow = document.createElement("tr");
      splitTableRow(header).forEach((cell) => {
        const heading = document.createElement("th");
        heading.textContent = cell;
        headingRow.append(heading);
      });
      tableHead.append(headingRow);
      table.append(tableHead);

      const tableBody = document.createElement("tbody");
      index += 2;
      while (index < lines.length && lines[index].includes("|")) {
        const row = document.createElement("tr");
        splitTableRow(lines[index]).forEach((cell) => {
          const data = document.createElement("td");
          data.textContent = cell;
          row.append(data);
        });
        tableBody.append(row);
        index += 1;
      }
      table.append(tableBody);
      wrapper.append(table);
      container.append(wrapper);
      index -= 1;
    } else {
      addTextLine(container, header);
    }
  }
}

async function readJson(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Something went wrong. Please try again.");
  return body;
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = questionInput.value.trim();
  if (!message) return;
  addMessage(message, "user");
  questionInput.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "Sending…";
  try {
    const response = await fetch(`${apiBaseUrl}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
    const data = await readJson(response);
    addMessage(data.answer, "assistant");
  } catch (error) {
    addMessage(error.message, "assistant");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "Send";
    questionInput.focus();
  }
});

document.getElementById("openLeadForm").addEventListener("click", () => leadDialog.showModal());
document.getElementById("closeLeadForm").addEventListener("click", () => leadDialog.close());

leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  leadStatus.textContent = "";
  const submitButton = document.getElementById("leadSubmit");
  submitButton.disabled = true;
  try {
    const payload = Object.fromEntries(new FormData(leadForm));
    const response = await fetch(`${apiBaseUrl}/api/leads`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const data = await readJson(response);
    leadStatus.className = "form-status success";
    leadStatus.textContent = data.message;
    leadForm.reset();
  } catch (error) {
    leadStatus.className = "form-status error";
    leadStatus.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
