from pyscript import document

MENU = [
    {
        "id": "margherita",
        "name": "Margherita",
        "desc": "San Marzano tomatoes, fresh mozzarella, basil, extra virgin olive oil.",
        "price_sm": 12.00,
        "price_lg": 16.00,
        "veg": True,
        "hot": False
    },
    {
        "id": "diavola",
        "name": "Diavola",
        "desc": "San Marzano tomatoes, mozzarella, spicy salami, nduja, chili oil.",
        "price_sm": 14.50,
        "price_lg": 19.00,
        "veg": False,
        "hot": True
    },
    {
        "id": "marinara",
        "name": "Marinara",
        "desc": "San Marzano tomatoes, garlic, oregano, extra virgin olive oil.",
        "price_sm": 10.00,
        "price_lg": 13.50,
        "veg": True,
        "hot": False
    },
    {
        "id": "funghi",
        "name": "Bosco",
        "desc": "Wild mushrooms, mozzarella, truffle paste, fresh parsley.",
        "price_sm": 15.00,
        "price_lg": 20.00,
        "veg": True,
        "hot": False
    }
]

def init_video_controls():
    video = document.getElementById("heroVid")
    mute_btn = document.getElementById("mute")
    
    if not video or not mute_btn:
        return

    def toggle_mute(event):
        if video.muted:
            video.muted = False
            mute_btn.innerText = "🔊"
            mute_btn.setAttribute("aria-label", "Mute video")
        else:
            video.muted = True
            mute_btn.innerText = "🔇"
            mute_btn.setAttribute("aria-label", "Unmute video")

    mute_btn.onclick = toggle_mute

init_video_controls()
