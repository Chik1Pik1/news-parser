// Подключаемся к Supabase
const SUPABASE_URL = "ТВОЙ_SUPABASE_URL";
const SUPABASE_KEY = "ТВОЙ_ANON_KEY"; // можно ограниченный anon key
const supabase = Supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

const newsContainer = document.getElementById("newsContainer");
const categorySelect = document.getElementById("categorySelect");
const nsfwToggle = document.getElementById("nsfwToggle");

async function loadCategories() {
  const { data, error } = await supabase.from("categories").select("*");
  if (error) return console.error(error);
  data.forEach(cat => {
    const option = document.createElement("option");
    option.value = cat.id;
    option.textContent = cat.title;
    categorySelect.appendChild(option);
  });
}

async function loadNews() {
  newsContainer.innerHTML = "";
  let query = supabase.from("news").select("*").order("published_at", { ascending: false }).limit(50);
  
  if (categorySelect.value) {
    query = query.eq("category_id", categorySelect.value);
  }
  if (!nsfwToggle.checked) {
    query = query.eq("is_nsfw", false);
  }

  const { data, error } = await query.execute();
  if (error) return console.error(error);

  data.forEach(item => {
    const div = document.createElement("div");
    div.className = "news-card";
    div.innerHTML = `<div class="news-title">${item.title}</div>
                     <div class="news-summary">${item.summary || ''}</div>
                     <a href="${item.url}" target="_blank">Читать далее</a>`;
    newsContainer.appendChild(div);
  });
}

categorySelect.addEventListener("change", loadNews);
nsfwToggle.addEventListener("change", loadNews);

loadCategories().then(loadNews);