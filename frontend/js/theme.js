// ================================
// Theme Manager
// ================================

const themeToggle = document.getElementById("themeToggle");
const themeStyle = document.getElementById("theme-style");
const themeIcon = themeToggle.querySelector("i");


// ================================
// Apply Theme
// ================================

function applyTheme(theme){

    if(theme === "dark"){

        themeStyle.href = "css/dark.css";

        themeIcon.classList.remove("fa-moon");
        themeIcon.classList.add("fa-sun");

    }

    else{

        themeStyle.href = "css/light.css";

        themeIcon.classList.remove("fa-sun");
        themeIcon.classList.add("fa-moon");

    }

}


// ================================
// Load Saved Theme
// ================================

const savedTheme = localStorage.getItem("theme");

if(savedTheme){

    applyTheme(savedTheme);

}
else{

    applyTheme("light");

}


// ================================
// Toggle Theme
// ================================

themeToggle.addEventListener("click",()=>{

    const currentTheme =
        themeStyle.getAttribute("href").includes("dark")
        ? "dark"
        : "light";

    const newTheme =
        currentTheme === "dark"
        ? "light"
        : "dark";

    applyTheme(newTheme);

    localStorage.setItem("theme",newTheme);

});