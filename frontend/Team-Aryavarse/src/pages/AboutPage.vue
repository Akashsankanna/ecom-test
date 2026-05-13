<template>
  <q-page class="about-page">

    <!-- ── HERO ── -->
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="container hero-content">
        <h1 ref="heroTitle">PARALLEL</h1>
        <p class="hero-kicker" data-anim style="transition-delay:0.5s">A Division of Pushpa Textile</p>
        <p class="hero-subtitle split-text" ref="heroSub" data-anim style="transition-delay:0.7s">
          Built on legacy, refined through quality, and designed for modern professional wear.
        </p>
      </div>
    </section>

    <!-- ── OUR STORY ── -->
    <section class="section">
      <div class="container story-grid">

        <div class="story-image-card" data-anim="left">
          <img :src="aboutImg('Hanger_scrubs.png')" />
        </div>

        <div class="story-content">
          <p class="section-label" data-anim>OUR STORY</p>
          <h2 class="split-text" data-anim style="transition-delay:0.1s">One of the pioneers of Solapur textile industry..</h2>

          <p data-anim style="transition-delay:0.12s">
            Incorporated in the year 1975, the first brick of "Pushpa Textile" was laid by Shri Sureshchandra Ramkisan Rathi at Solapur, Maharashtra India under the chairmanship of Shri Ramkisan Rathi.
            It started with 12 looms, Pushpa Textile operates a complete in-house manufacturing unit of Jacquard Design Solapuri Chaddars and Turkish Towels.
          </p>

          <p data-anim style="transition-delay:0.22s">
            Since then company has made rapid progress having 200 looms at 5 processing units today. Now, we have grown to a brand for the apparel industry, Hotel and Hospital Linen Range, Corporate and School Uniforms, Jute Bags, Printed Bedsheets and so much more. All this made at our new factory with new age machinery to be the textile company you trust and love using.
            At Pushpa Textile, we always look forward maintaining quality and honoring its commitments..
          </p>

          <p data-anim style="transition-delay:0.32s">
            Parallel — A Division of Pushpa Textile — carries this same foundation forward with a more
            contemporary approach. It combines years of manufacturing experience
            with modern design thinking to create apparel that is functional,
            durable, and professionally refined.
          </p>
        </div>
      </div>
    </section>

    <!-- ── 50 YEARS ── -->
    <section class="section light-section">
      <div class="container">
        <div class="section-heading center">
          <p class="section-label" data-anim>50 YEARS OF TEXTILE EXCELLENCE</p>
          <h2 class="split-text" data-anim style="transition-delay:0.1s">Manufacturing strength with premium presentation.</h2>
          <p class="section-intro" data-anim style="transition-delay:0.2s">
            Our process is built on quality control, structured production,
            precision finishing, and a deep understanding of textile performance.
          </p>
        </div>

        <div class="feature-grid">
          <div class="feature-card" data-anim="scale" style="transition-delay:0.05s">
            <div class="feature-icon">01</div>
            <h3>Quality First</h3>
            <p>
              Every stage of production is guided by consistency, attention to
              detail, and dependable finishing standards.
            </p>
          </div>

          <div class="feature-card" data-anim="scale" style="transition-delay:0.15s">
            <div class="feature-icon">02</div>
            <h3>Modern Production</h3>
            <p>
              We combine manufacturing discipline with updated processes to
              deliver apparel that meets present-day professional needs.
            </p>
          </div>

          <div class="feature-card" data-anim="scale" style="transition-delay:0.25s">
            <div class="feature-icon">03</div>
            <h3>Functional Design</h3>
            <p>
              Our products are developed with comfort, durability, and practical
              usability in mind for modern work environments.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── VALUES ── -->
    <section class="section soft-section">
      <div class="container values-grid">
        <div class="value-card" data-anim="left">
          <p class="section-label">OUR PLEDGE</p>
          <h3>Trusted quality in every product.</h3>
          <p>
            We are committed to delivering products that reflect quality India Textile,
            consistency, and professional reliability in both design and finish.
          </p>
        </div>

        <div class="value-card" data-anim="right">
          <p class="section-label">OUR MISSION</p>
          <h3>To build modern apparel with strong textile roots.</h3>
          <p>
            Our mission is to combine legacy manufacturing strength with
            innovation, comfort, and refined product development for evolving
            professional industries.
          </p>
        </div>
      </div>
    </section>

    <!-- ── MANAGEMENT ── -->
    <section class="section">
      <div class="container section-heading">
        <p class="section-label" data-anim>MANAGEMENT</p>
        <h2 class="split-text" data-anim style="transition-delay:0.1s">Our Management</h2>
        <p class="section-intro leadership-intro" data-anim style="transition-delay:0.2s">
          The strength of Parallel lies in the people who continue to guide the
          brand with vision, discipline, and long-term commitment to excellence.
        </p>
      </div>

      <div class="container leadership-grid">
        <div
          class="leader-card"
          data-anim="scale"
          v-for="(member, i) in team"
          :key="member.name"
          :style="{ transitionDelay: (i * 0.1) + 's' }"
        >
          <div class="leader-image-wrap">
            <img :src="member.image" class="leader-image" />
          </div>
          <div class="leader-body">
            <h4>{{ member.name }}</h4>
            <p class="leader-role">{{ member.role }}</p>
            <p class="leader-desc">{{ member.desc }}</p>
          </div>
        </div>
      </div>
    </section>

  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { aboutImg } from 'src/data/imageHelper'

const heroTitle = ref(null)
const heroSub = ref(null)

const team = [
  {
    name: 'Sureshchandra Rathi',
    role: 'Founder',
    image: aboutImg('sureshchandra.png'),
    desc: 'The Person who laid the first Bricks of Pushpa Textile. Starting with power looms and the manufacturing of the Solapur Chaddar. His hard work, dedication and vision has brought growth and expansion over the years.'
  },
  {
    name: 'Prashant Rathi',
    role: 'Director',
    image: aboutImg('prashant.png'),
    desc: 'He started the Garment division of our firm. And built a Brand around Pushpa Textile and those associated with it. With his zeal and enthusiasm, he ensure quality and timely delivery. He studied at Symbiosis Pune and did his MBA at Sydney.'
  },
  {
    name: 'Sapna Rathi',
    role: 'Operations',
    image: aboutImg('sapna.png'),
    desc: 'She brings her expertise in to execute on the ground operations and create sustainable processes in house for our Garment Unit. She is an MBA graduate from Pune with experience working with IT companies for ISO Processes.'
  },
  {
    name: 'Pankaj Rathi',
    role: 'Management',
    image: aboutImg('pankaj.png'),
    desc: 'He manages our Overseas Operations. He graduated from VJTI Mumbai as Gold Medalist in Textile Engineering & completed Masters degree in Textiles & Supply Chain from Cornell University, NY. Currently based in Houstan Texas and leading a Global Shipping Business.'
  }
]

onMounted(() => {
  /* ── char-by-char hero h1 ── */
  if (heroTitle.value) {
    const el = heroTitle.value
    const text = el.textContent
    el.innerHTML = text.split('').map((c, i) =>
      `<span class="char" style="transition-delay:${(0.1 + i * 0.055).toFixed(2)}s">${c === ' ' ? '&nbsp;' : c}</span>`
    ).join('')
    el.classList.add('char-reveal')
    requestAnimationFrame(() => el.classList.add('anim-in'))
  }

  /* ── word-by-word split text ── */
  document.querySelectorAll('.split-text').forEach(el => {
    // skip if already split
    if (el.querySelector('.word')) return
    const nodes = Array.from(el.childNodes)
    el.innerHTML = ''
    nodes.forEach(node => {
      if (node.nodeType === 3) {
        // text node — split into words
        node.textContent.split(/(\s+)/).forEach((chunk, ci) => {
          if (/^\s+$/.test(chunk)) {
            el.appendChild(document.createTextNode(chunk))
          } else {
            const span = document.createElement('span')
            span.className = 'word'
            span.style.transitionDelay = (ci * 0.04) + 's'
            span.textContent = chunk
            el.appendChild(span)
          }
        })
      } else {
        el.appendChild(node.cloneNode(true))
      }
    })
  })

  /* ── IntersectionObserver for all animated elements ── */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('anim-in')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.13 })

  // data-anim elements
  document.querySelectorAll('[data-anim]').forEach(el => observer.observe(el))

  // split-text headings
  document.querySelectorAll('.split-text').forEach(el => observer.observe(el))

  // section-label underline draw
  document.querySelectorAll('.section-label').forEach(el => observer.observe(el))

  /* ── trigger elements already in viewport on load ── */
  setTimeout(() => {
    const allTargets = document.querySelectorAll('[data-anim], .split-text, .section-label')
    allTargets.forEach(el => {
      const rect = el.getBoundingClientRect()
      if (rect.top < window.innerHeight * 0.95) {
        el.classList.add('anim-in')
      }
    })
  }, 80)
})
</script>

<style lang="scss">
@import "src/css/about.scss";
</style>