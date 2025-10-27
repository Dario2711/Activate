// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById("mobileMenuBtn")
const mobileNav = document.getElementById("mobileNav")

mobileMenuBtn.addEventListener("click", () => {
  mobileMenuBtn.classList.toggle("active")
  mobileNav.classList.toggle("active")
})

// Close mobile menu when clicking on a link
const mobileNavLinks = mobileNav.querySelectorAll("a")
mobileNavLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mobileMenuBtn.classList.remove("active")
    mobileNav.classList.remove("active")
  })
})

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  })
})

// Add scroll effect to navbar
let lastScroll = 0
const navbar = document.querySelector(".navbar")

window.addEventListener("scroll", () => {
  const currentScroll = window.pageYOffset

  if (currentScroll > 100) {
    navbar.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.15)"
  } else {
    navbar.style.boxShadow = "0 2px 10px rgba(0, 0, 0, 0.1)"
  }

  lastScroll = currentScroll
})

document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card")

  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "0"
        entry.target.style.transform = "translateY(30px)"

        setTimeout(() => {
          entry.target.style.transition = "opacity 0.6s ease, transform 0.6s ease"
          entry.target.style.opacity = "1"
          entry.target.style.transform = "translateY(0)"
        }, 100)

        observer.unobserve(entry.target)
      }
    })
  }, observerOptions)

  cards.forEach((card) => {
    observer.observe(card)
  })
})
