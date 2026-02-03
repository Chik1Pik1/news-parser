const SUPABASE_URL = "https://rltppxkgyasyfkftintn.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJsdHBweGtneWFzeWZrZnRpbnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNTM0NDAsImV4cCI6MjA4NTYyOTQ0MH0.98RP1Ci9UFkjhKbi1woyW5dbRbXJ8qNdopM1aJMSdf4";

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const newsContainer = document.getElementById("news");

async function loadNews() {
  const { data, error } = await supabase
    .from("news")
    .select("id, title, url, published_at, is_nsfw")
    .order("published_at", { ascending: false })
    .limit(50);

  if (error) {
    console.error("Ошибка загрузки новостей:", error);
    newsContainer.innerHTML = "<p>Ошибка загрузки новостей</p>";
    return;
  }

  if (!data || data.length === 0) {
    newsContainer.innerHTML = "<p>Новостей пока нет</p>";
    return;
  }

  newsContainer.innerHTML = "";

  data.forEach(item => {
    const card = document.createElement("div");
    card.className = "news-card";

    card.innerHTML = `
      <h3>${item.title}</h3>
      <small>${item.published_at ? new Date(item.published_at).toLocaleString() : ""}</small>
      <br/><br/>
      <a href="${item.url}" target="_blank">Читать →</a>
    `;

    newsContainer.appendChild(card);
  });
}

loadNews();