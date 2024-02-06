/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./custom/**/*.{html,js,xml}"],
    theme: {
        extend: {},
    },
    blocklist: ["container", "collapse"], 
    plugins: [require("daisyui")],
};
