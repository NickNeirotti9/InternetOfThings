window.addEventListener('DOMContentLoaded', () => {

document.getElementById('summarize-btn').addEventListener('click', async e => {
      e.preventDefault();
      const form = document.getElementById('audio-actions');
      const checked = Array.from(form.querySelectorAll('input[name="files"]:checked')); //gets selected files
      const progressEl = document.getElementById('progress');
      progressEl.innerHTML = ''; // clears messages

      if (checked.length === 0) {
        alert("No files selected.");
        return;
      } 

      document.getElementById('summarize-btn').disabled = true; //Disables buttons while summarizing
      document.getElementById('archive-btn').disabled = true;

      for (let cb of checked) { 
        const file = cb.value; //Loops through files

        //Transcribe step:
        let p1 = document.createElement('p');
        p1.textContent = `Transcribing ${file}…`;
        progressEl.appendChild(p1);

        let res1 = await fetch(BF.transcribeOne, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file })
        });
        let j1 = await res1.json();
        p1.textContent = j1.success
          ? `Transcribed ${file}`
          : `${j1.message}`;

        //Summarize step:
        let p2 = document.createElement('p');
        p2.textContent = `Summarizing ${file}…`;
        progressEl.appendChild(p2);

        let res2 = await fetch(BF.summarizeOne, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file })
        });
        let j2 = await res2.json();
        p2.textContent = j2.success
          ? `Summarized ${file}`
          : `${j2.message}`;
      }
    
      document.getElementById('summarize-btn').disabled = false; // Re-enable buttons
      document.getElementById('archive-btn').disabled = false;

      let done = document.createElement('p'); //display process is complete
      done.innerHTML = `All done! Summarized ${checked.map(cb => cb.value).join(', ')}`;
      progressEl.appendChild(done);
      await updateRecentNotes(); //refresh UI
      await updateAvailableAudio();
    });

async function updateRecentNotes() {
    try {
      const res = await fetch(BF.recentNotes);
      const notes = await res.json();
      
      const ul = document.createElement('ul');
      ul.id = 'recent-notes-list';

      if (notes.length === 0) {
        ul.innerHTML = '<li>No notes yet.</li>';
      } else {
        for (let n of notes) {
          const li = document.createElement('li');
          li.innerHTML = `
            <a href="/note/${n.filename}"><strong>${n.title}</strong></a>
            <small>(${n.date} | ${n.category})</small><br>
            <em>${n.summary}</em>`;
          ul.appendChild(li);
        }
      }
      document.getElementById('recent-notes-list').replaceWith(ul); // Swap old list for new
    } catch (err) {
      console.error("Failed to update recent notes:", err);
    }
  }

  async function updateAvailableAudio() {
    try {
      const res = await fetch(BF.availableAudio);
      const files = await res.json();
      const listDiv = document.getElementById('audio-list');
      listDiv.innerHTML = '';  // clear

      if (files.length === 0) {
        listDiv.innerHTML = '<p>No audio pending.</p>';
      } else {
        files.forEach(f => {
          const lbl = document.createElement('label');
          lbl.innerHTML = `<input type="checkbox" name="files" value="${f}">${f}<br>`;
          listDiv.appendChild(lbl);
        });
      }
    } catch (err) {
      console.error("Failed to update available audio:", err);
    }
  }

const syncForm = document.getElementById('sync-form');
if (syncForm) {
  const syncBtn     = document.getElementById('sync-btn');
  const syncSpinner = document.getElementById('sync-spinner');
  syncForm.addEventListener('submit', () => {
    syncBtn.disabled          = true;
    syncSpinner.style.display = 'inline';
  });
}

});

function toggleAll(master, formId) { //select all button functionality (only works outside of DOM event)
      const form = document.getElementById(formId);
      if (!form) return;
      form.querySelectorAll('input[type=checkbox][name=files]').forEach(cb => cb.checked = master.checked);
    }