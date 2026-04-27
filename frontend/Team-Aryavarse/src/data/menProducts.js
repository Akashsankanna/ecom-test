// ============================================================
// menProducts.js – new file structure + backend variant_id added
// ============================================================

import { parallelImg, modelImg, collarBoyImg } from './imageHelper'

export const menProducts = [
  {
    id: 101,
    title: "Classic Men's Collar Scrub",
    price: 999.00,
    oldPrice: 1200.00,
    rating: 4.8,
    fabric: "Classic",
    color: "brown",
    type: "men",
    category: "Scrubs",
    isBestSeller: true,
    description: "Premium classic collar scrub designed for healthcare professionals who prefer a structured and polished look.",
    details: [
      "Smart collar neck design for formal professional appearance",
      "Relaxed fit for easy movement during long shifts",
      "Multiple roomy pockets for essentials and accessories",
      "Tailored stitching for structured fitting",
      "Perfect blend of comfort and style for everyday hospital wear"
    ],
    fabricDescription: "Crafted with premium Classic fabric that provides durability, softness, and breathable comfort throughout your workday.",
    fabricCare: [
      "75% Poly", "25% Viscose",
      "Soft breathable classic weave fabric",
      "Machine wash cold with like colors",
      "Do not bleach or tumble dry"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('brown_and_light_brown.png'),
    images: [
      parallelImg('brown_and_light_brown.png'),
      modelImg('brothers_suit.png'),
    ],
    colors: [
      {
        name: "brown",
        hex: "#964B00",
        variant_id: 54,
        images: [
          parallelImg('brown_and_light_brown.png'),
          modelImg('brothers_suit.png'),
        ]
      },
      {
        name: "green",
        hex: "#006400",
        variant_id: 52,
        images: [
          parallelImg('Dark_green.png'),
          modelImg('Dark_Green_full_sleeves.png'),
        ]
      },
    ]
  },

  {
    id: 102,
    title: "ecoflex™ Men's Longsleeves Scrub",
    price: 1050.00,
    oldPrice: 1400.00,
    rating: 4.7,
    fabric: "Ecoflex",
    color: "Green",
    type: "men",
    category: "Scrubs",
    isBestSeller: true,
    description: "Advanced Ecoflex long sleeve scrub designed for superior flexibility, comfort, and modern professional styling.",
    details: [
      "Full sleeve coverage for enhanced protection",
      "Modern zip-front closure for stylish appearance",
      "Flexible stretchable design for active movement",
      "Deep utility pockets for convenience",
      "Perfect for long working hours and busy schedules"
    ],
    fabricDescription: "Made from lightweight Ecoflex stretch fabric engineered for flexibility, moisture control, and all-day performance.",
    fabricCare: [
      "80% Poly", "20% Spandex Blend",
      "4-way stretch Ecoflex material",
      "Machine wash gentle cycle",
      "Do not iron on high heat"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('Dark_green.png'),
    images: [
      parallelImg('Dark_green.png'),
      modelImg('Dark_Green_full_sleeves.png'),
    ],
    colors: [
      {
        name: "Green",
        hex: "#006400",
        variant_id: 55,
        images: [
          parallelImg('Dark_green.png'),
          modelImg('Dark_Green_full_sleeves.png'),
        ]
      },
      {
        name: "Navy Blue",
        hex: "#000080",
        variant_id: 57,
        images: [
          parallelImg('Navy_blue_full_sleeves.png'),
          modelImg('Navy_blue_full_sleeves.png'),
        ]
      }
    ]
  },

  {
    id: 103,
    title: "Classic Men Longsleeves Scrub Set",
    price: 1050.00,
    oldPrice: 1400.00,
    rating: 4.6,
    fabric: "Classic",
    color: "Grey",
    type: "men",
    category: "Scrubs",
    description: "Classic long sleeve scrub set designed with full coverage and structured comfort for professional medical use.",
    details: [
      "Elegant long sleeve design for added protection",
      "Structured stitching for polished appearance",
      "Breathable fit for all-day comfort",
      "Functional side and chest pockets",
      "Ideal for clinics, labs, and hospitals"
    ],
    fabricDescription: "Premium Classic fabric offers breathable comfort and durable wear suitable for daily professional use.",
    fabricCare: [
      "75% Poly", "25% Cotton Blend",
      "Wrinkle-resistant material",
      "Machine washable",
      "Do not bleach"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('Grey.png'),
    images: [
      parallelImg('Grey.png'),
    ],
    colors: [
      {
        name: "Grey",
        hex: "#808080",
        variant_id: 59,
        images: [
          parallelImg('Grey.png')
        ]
      },
      {
        name: "Green",
        hex: "#006400",
        variant_id: 58,
        images: [
          parallelImg('Dark_green.png'),
          modelImg('Dark_Green_full_sleeves.png'),
        ]
      },
      {
        name: "Navy Blue",
        hex: "#000080",
        variant_id: 60,
        images: [
          parallelImg('Navy_blue_full_sleeves.png'),
          modelImg('Navy_blue_full_sleeves.png'),
        ]
      },
      {
        name: "Mustard Yellow",
        hex: "#FFCB05",
        variant_id: 61,
        images: [
          parallelImg('mustard_yellow_scrub.png'),
          modelImg('Mustard_yellow_scrub_suit.png'),
        ]
      },
      {
        name: "Mint Green",
        hex: "#98FB98",
        variant_id: 62,
        images: [
          parallelImg('Mint_green_full_sleevs.png'),
          modelImg('Mint_green_full_sleeves_scrub.png'),
        ]
      },
      {
        name: "Maroon",
        hex: "#800000",
        variant_id: 63,
        images: [
          parallelImg('maroon_scrub.png'),
          modelImg('Maroon_scrub_suit.png'),
        ]
      }
    ]
  },

  {
    id: 104,
    title: "ecoflex™ Men's Round-Neck Scrub",
    price: 600.00,
    oldPrice: 800.00,
    rating: 4.9,
    fabric: "Ecoflex",
    color: "Soft Blue+Grey",
    type: "men",
    category: "Scrubs",
    description: "Premium Ecoflex round-neck scrub designed for modern professionals seeking flexibility, comfort, and sleek everyday styling.",
    details: [
      "Modern round-neck design for clean minimal look",
      "Stretch-fit tailoring for unrestricted movement",
      "Breathable lightweight structure for long shifts",
      "Multiple utility pockets for convenience",
      "Ideal for hospital, clinic, and lab environments"
    ],
    fabricDescription: "Made using premium Ecoflex stretch fabric that offers softness, flexibility, and moisture-wicking comfort all day long.",
    fabricCare: [
      "80% Poly", "20% Spandex Blend",
      "4-way stretch breathable Ecoflex material",
      "Machine wash cold",
      "Do not bleach or iron directly"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('Round_neck_blue+grey_scrub_suit_men.png'),
    images: [
      parallelImg('Round_neck_blue+grey_scrub_suit_men.png'),
      modelImg('Grey+blue_scrub.png'),
    ],
    colors: [
      {
        name: "Soft Blue+Grey",
        hex: "#6699CC",
        variant_id: 64,
        images: [
          parallelImg('Round_neck_blue+grey_scrub_suit_men.png'),
          modelImg('Grey+blue_scrub.png'),
        ]
      },
      {
        name: "Mint Green",
        hex: "#98FB98",
        variant_id: 65,
        images: [
          parallelImg('Mint_green_full_sleevs.png'),
          modelImg('Mint_green_full_sleeves_scrub.png'),
        ]
      },
      {
        name: "brown",
        hex: "#964B00",
        variant_id: 66,
        images: [
          parallelImg('brown_and_light_brown.png'),
          modelImg('brothers_suit.png'),
        ]
      }
    ]
  },

  {
    id: 105,
    title: "Classic Men's Collar Scrub",
    price: 999.00,
    oldPrice: 1200.00,
    rating: 4.7,
    fabric: "Classic",
    color: "Maroon",
    type: "men",
    category: "Scrubs",
    isBestSeller: true,
    description: "Professional surgical scrub with classic collar styling designed for superior comfort and polished clinical appearance.",
    details: [
      "Structured collar neckline for elegant professional styling",
      "Relaxed fit allows smooth movement during procedures",
      "Spacious pockets for medical essentials",
      "Durable stitching for long-lasting wear",
      "Perfect for surgical and hospital professionals"
    ],
    fabricDescription: "Constructed with durable Classic fabric for breathable softness, wrinkle resistance, and long-term daily wear.",
    fabricCare: [
      "75% Poly", "25% Viscose",
      "Soft-touch wrinkle resistant fabric",
      "Wash separately in cold water",
      "Do not tumble dry"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('maroon_scrub.png'),
    images: [
      parallelImg('maroon_scrub.png'),
      modelImg('Maroon_scrub_suit.png'),
    ],
    colors: [
      {
        name: "Maroon",
        hex: "#6b1a2a",
        variant_id: 67,
        images: [
          parallelImg('maroon_scrub.png'),
          modelImg('Maroon_scrub_suit.png'),
        ]
      },
      {
        name: "Mustard Yellow",
        hex: "#FFCB05",
        variant_id: 68,
        images: [
          parallelImg('mustard_yellow_scrub.png'),
          modelImg('Mustard_yellow_scrub_suit.png'),
        ]
      },
    ]
  },

  {
    id: 106,
    title: "ecoflex™ Men's Round-Neck Scrub",
    price: 800.00,
    oldPrice: 1000.00,
    rating: 4.8,
    fabric: "Ecoflex",
    color: "Mint Green",
    type: "men",
    category: "Scrubs",
    description: "Lightweight Ecoflex round-neck scrub crafted for breathable comfort and effortless movement during demanding shifts.",
    details: [
      "Classic round-neck design for modern appearance",
      "Stretch-fit comfort for active professionals",
      "Breathable material reduces heat build-up",
      "Functional utility pockets for convenience",
      "Ideal for long hospital and clinic shifts"
    ],
    fabricDescription: "Crafted from advanced Ecoflex performance fabric that combines stretch, breathability, and lightweight comfort.",
    fabricCare: [
      "80% Poly", "20% Spandex Blend",
      "Lightweight breathable stretch fabric",
      "Gentle machine wash recommended",
      "Avoid high-temperature drying"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('Mint_green_full_sleevs.png'),
    images: [
      parallelImg('Mint_green_full_sleevs.png'),
      modelImg('Mint_green_full_sleeves_scrub.png'),
    ],
    colors: [
      {
        name: "Mint Green",
        hex: "#98FB98",
        variant_id: 69,
        images: [
          parallelImg('Mint_green_full_sleevs.png'),
          modelImg('Mint_green_full_sleeves_scrub.png'),
        ]
      },
      {
        name: "Tan",
        hex: "#D2B48C",
        variant_id: 70,
        images: [
          parallelImg('Tan_color_full_sleevs_scrub_men.png'),
          modelImg('Tan_color_full_sleeves_scrub.png'),
        ]
      },
      {
        name: "Yellow",
        hex: "#FFFF00",
        variant_id: 71,
        images: [
          parallelImg('yellow_full_sleeve_scrub_suit_men.png'),
          modelImg('light_yellow_full_sleeves_scrub.png'),
        ]
      }
    ]
  },

  {
    id: 107,
    title: "ecoflex™ Men's V-Neck Scrub",
    price: 850.00,
    oldPrice: 1100.00,
    rating: 4.8,
    fabric: "Classic",
    color: "Navy Green",
    type: "men",
    category: "Scrubs",
    description: "Stylish V-neck scrub tailored for modern healthcare professionals who value flexibility and professional comfort.",
    details: [
      "Modern V-neck design for sharp professional styling",
      "Relaxed ergonomic fit for all-day wear",
      "Easy movement construction for active shifts",
      "Functional pockets for storage needs",
      "Ideal for clinics, hospitals, and healthcare staff"
    ],
    fabricDescription: "Premium Classic comfort fabric ensures breathable softness, durability, and wrinkle-resistant everyday wear.",
    fabricCare: [
      "75% Poly", "25% Viscose",
      "Breathable lightweight classic weave",
      "Machine wash cold",
      "Do not bleach"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: parallelImg('Vneck_dark_green_scrub_suit_men.png'),
    images: [
      parallelImg('Vneck_dark_green_scrub_suit_men.png'),
      modelImg('V_neck_Dark_green_scrub.png'),
    ],
    colors: [
      {
        name: "Navy Green",
        hex: "#006400",
        variant_id: 73,
        images: [
          parallelImg('Vneck_dark_green_scrub_suit_men.png'),
          modelImg('V_neck_Dark_green_scrub.png'),
        ]
      },
      {
        name: "Tan color",
        hex: "#C4A484",
        variant_id: 74,
        images: [
          parallelImg('Vneck_scrub_suit_men.png'),
          modelImg('V_neck_Tan_color_scrub.png'),
        ]
      }
    ]
  },

  {
    id: 108,
    title: "ecoflex™ Lite Men's Collar Scrub",
    price: 999.00,
    oldPrice: 1200.00,
    fabric: "Ecoflex Lite",
    color: "Black",
    rating: 4.7,
    type: "men",
    category: "Scrubs",
    isBestSeller: true,
    description: "Ultra-light Ecoflex Lite collar scrub built for breathable comfort, lightweight feel, and effortless professional styling.",
    details: [
      "Classic collar design for polished appearance",
      "Ultra-lightweight build for extra comfort",
      "Flexible fit for unrestricted movement",
      "Utility pockets for practical storage",
      "Perfect for everyday healthcare wear"
    ],
    fabricDescription: "Made from Ecoflex Lite performance fabric offering feather-light comfort, flexibility, and breathable softness.",
    fabricCare: [
      "82% Poly", "18% Spandex Blend",
      "Ultra-light Ecoflex Lite stretch material",
      "Machine wash gentle",
      "Do not use strong bleach"
    ],
    returnDescription: "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      "Embroidery products are not eligible for return or exchange.",
      "Items that have been used, washed, or had their tags removed cannot be returned.",
      "Orders placed during sale events are final and not eligible for return but can be exchanged."
    ],
    image: collarBoyImg('Black1.png'),
    images: [
      collarBoyImg('Black1.png'),
      collarBoyImg('Black2.png'),
      collarBoyImg('Black3.png'),
    ],
    colors: [
      {
        name: "Black",
        hex: "#000000",
        variant_id: 72,
        images: [
          collarBoyImg('Black1.png'),
          collarBoyImg('Black2.png'),
          collarBoyImg('Black3.png'),
        ],
      },
      {
        name: "Blue",
        hex: "#ADD8E6",
        variant_id: 75,
        images: [
          collarBoyImg('Blue1.png'),
          collarBoyImg('Blue2.png'),
          collarBoyImg('Light_Blue3.png'),
        ],
      },
      {
        name: "Brown",
        hex: "#964B00",
        variant_id: 58,
        images: [
          collarBoyImg('Brown1.png'),
          collarBoyImg('Brown2.png'),
          collarBoyImg('Brown3.png'),
        ],
      },
      {
        name: "Dark Grey",
        hex: "#A9A9A9",
        variant_id: 76,
        images: [
          collarBoyImg('Dark_Grey1.png'),
          collarBoyImg('Dark_Grey2.png'),
          collarBoyImg('Dark_Grey3.png'),
        ],
      },
      {
        name: "Green",
        hex: "#008000",
        variant_id: 77,
        images: [
          collarBoyImg('Green1.png'),
          collarBoyImg('Green2.png'),
          collarBoyImg('Green3.png'),
        ],
      },
      {
        name: "Navy blue",
        hex: "#000080",
        variant_id: 78,
        images: [
          collarBoyImg('Navy_blue1.png'),
          collarBoyImg('Navy_blue2.png'),
          collarBoyImg('Navy_blue3.png'),
        ],
      },
    ]
  },
]
