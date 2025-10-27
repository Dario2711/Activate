// Mobile Menu Toggle (same behavior as main page)
const mobileMenuBtn = document.getElementById("mobileMenuBtn")
const mobileNav = document.getElementById("mobileNav")

if (mobileMenuBtn && mobileNav) {
  mobileMenuBtn.addEventListener("click", () => {
    mobileMenuBtn.classList.toggle("active")
    mobileNav.classList.toggle("active")
  })

  const mobileNavLinks = mobileNav.querySelectorAll("a")
  mobileNavLinks.forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenuBtn.classList.remove("active")
      mobileNav.classList.remove("active")
    })
  })
}

// Add scroll effect to navbar
const navbar = document.querySelector(".navbar")
if (navbar) {
  window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset
    if (currentScroll > 100) {
      navbar.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.15)"
    } else {
      navbar.style.boxShadow = "0 2px 10px rgba(0, 0, 0, 0.1)"
    }
  })
}

// Download palette as CSS file
const downloadBtn = document.getElementById("downloadPalette")
if (downloadBtn) {
  downloadBtn.addEventListener("click", () => {
    const root = document.documentElement
    const styles = getComputedStyle(root)

    const vars = [
      "--primary-blue",
      "--secondary-blue",
      "--accent-cyan",
      "--text-dark",
      "--text-light",
      "--bg-light",
      "--white",
      "--black",
    ]

    const lines = vars.map((v) => {
      const val = styles.getPropertyValue(v).trim()
      return `  ${v}: ${val};`
    })

    const css = `:root{\n${lines.join("\n")}\n}`

    const blob = new Blob([css], { type: "text/css" })
    const url = URL.createObjectURL(blob)

    const a = document.createElement("a")
    a.href = url
    a.download = "palette.css"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  })
}
