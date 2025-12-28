const BASE_URL = "http://127.0.0.1:8000";

async function loadSites() {
    const list = document.getElementById("sitesList");
    list.innerHTML = "⏳ Loading...";
    try {
        const res = await axios.get(`${BASE_URL}/sites`);
        const data = res.data;
        if (data.length === 0) list.innerHTML = "<p>No sites found.</p>";
        else {
            list.innerHTML = data.map(site =>
                `<li class="border p-3 rounded-lg">
                    <h3 class="font-semibold">${site.name}</h3>
                    <p class="text-sm text-gray-600">${site.description || "No description"}</p>
                    <p class="text-xs text-gray-500">${site.location || "Location N/A"}</p>
                </li>`
            ).join("");
        }
    } catch (err) {
        list.innerHTML = `<p class='text-red-500'>Error loading sites: ${err}</p>`;
    }
}

async function loadOralHistories() {
    const list = document.getElementById("oralList");
    list.innerHTML = "⏳ Loading...";
    try {
        const res = await axios.get(`${BASE_URL}/oral-histories`);
        const data = res.data.data;
        if (data.length === 0) list.innerHTML = "<p>No oral histories found.</p>";
        else {
            list.innerHTML = data.map(item =>
                `<li class="border p-3 rounded-lg">
                    <h3 class="font-semibold">${item.title || "Untitled"}</h3>
                    <p class="text-sm text-gray-600">${item.story || "No story"}</p>
                </li>`
            ).join("");
        }
    } catch (err) {
        list.innerHTML = `<p class='text-red-500'>Error loading histories: ${err}</p>`;
    }
}

// Load initial data
window.onload = () => {
    loadSites();
    loadOralHistories();
};
