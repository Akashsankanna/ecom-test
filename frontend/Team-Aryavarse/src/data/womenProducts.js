import {
  collarGirlImg,
  vNeckModelImg,
  vNeckSideImg,
  vNeckHangerImg,
  parallelImg,
  modelImg,
} from './imageHelper'

export const womenProducts = [
  {
    id: 1,
    variant_id: 101,
    title: "Classic Women's V-Neck Scrub",
    category: 'Scrubs',
    fabric: 'Classic',
    color: 'Black',
    price: 999.0,
    oldPrice: 1200.0,
    rating: 4.5,
    type: 'women',
    isBestSeller: true,
    image: collarGirlImg('Black1.png'),
    images: [
      collarGirlImg('Black1.png'),
      collarGirlImg('Black(s)2.png'),
      collarGirlImg('black3.png'),
    ],
    colors: [
      {
        name: 'Black',
        hex: '#000000',
        variant_id: 101,
        images: [
          collarGirlImg('Black1.png'),
          collarGirlImg('Black(s)2.png'),
          collarGirlImg('black3.png'),
        ],
      },
      {
        name: 'Blue',
        hex: '#0000FF',
        images: [
          collarGirlImg('Blue1.png'),
          collarGirlImg('blue2.png'),
          collarGirlImg('blue3.png'),
        ],
      },
      {
        name: 'Green',
        hex: '#006400',
        images: [
          collarGirlImg('Green1.png'),
          collarGirlImg('Green2.png'),
          collarGirlImg('Green3.png'),
        ],
      },
      {
        name: 'Brown',
        hex: '#964B00',
        images: [
          collarGirlImg('Brown1.png'),
          collarGirlImg('Brown2.png'),
          collarGirlImg('Brown3.png'),
        ],
      },
      {
        name: 'Dark Grey',
        hex: '#A9A9A9',
        images: [
          collarGirlImg('Dark_Grey1.png'),
          collarGirlImg('Dark_Grey2.png'),
          collarGirlImg('Dark_grey3.png'),
        ],
      },
      {
        name: 'Navy Blue',
        hex: '#000080',
        images: [
          collarGirlImg('Navy_blue1.png'),
          collarGirlImg('Navy_blue2.png'),
          collarGirlImg('Navy_blue3.png'),
        ],
      },
    ],
    description:
      'Premium Classic V-Neck scrub designed for healthcare professionals who prefer comfort, elegance, and professional styling.',
    details: [
      'Modern V-Neck gives you room to move freely',
      'Roomy pockets for all essentials',
      'Side slits on the top for easy movement',
      'Loop ring to hold your ID badge',
      'Back darts for a more structured fit',
      'Classic, practical, and always professional',
    ],
    fabricDescription:
      'Crafted with premium Classic fabric that provides durability, softness, and breathable comfort throughout your workday.',
    fabricCare: [
      '75% Poly',
      '25% Viscose',
      'Wash inside out with like colors in 40°C water',
      'Do not bleach',
      'Only tumble dry',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 2,
    variant_id: 102,
    title: "Classic Women's V-Neck Scrub",
    category: 'Scrubs',
    fabric: 'Classic',
    color: 'Dark Green',
    price: 850.0,
    oldPrice: 1100.0,
    rating: 4.5,
    type: 'women',
    isBestSeller: true,
    image: vNeckModelImg('dark_green1.png'),
    images: [
      vNeckModelImg('dark_green1.png'),
      vNeckSideImg('dark_green2.png'),
      vNeckHangerImg('dark_green3.png'),
    ],
    colors: [
      {
        name: 'Dark Green',
        hex: '#013220',
        variant_id: 102,
        images: [
          vNeckModelImg('dark_green1.png'),
          vNeckSideImg('dark_green2.png'),
          vNeckHangerImg('dark_green3.png'),
        ],
      },
      {
        name: 'Blue',
        hex: '#00008B',
        images: [
          vNeckModelImg('vdark_blue.png'),
          vNeckSideImg('Vneck_dark_blue.png'),
          vNeckHangerImg('Dark_blue_scrub.png'),
        ],
      },
      {
        name: 'Green',
        hex: '#006400',
        images: [
          vNeckModelImg('Vneck_green.png'),
          vNeckSideImg('Vneck_green_scrub.png'),
          vNeckHangerImg('Green_medical_scrub_suit.png'),
        ],
      },
      {
        name: 'Dust Pink',
        hex: '#D58A94',
        images: [
          vNeckModelImg('Vneck_pink.png'),
          vNeckSideImg('dust_pink.png'),
          vNeckHangerImg('Pink_scrub.png'),
        ],
      },
      {
        name: 'Mint Green',
        hex: '#98FB98',
        images: [
          vNeckModelImg('Vneck_mint_green.png'),
          vNeckSideImg('Vneck_mint_green.png'),
          vNeckHangerImg('Mint_green_medical_scrub_set.png'),
        ],
      },
      {
        name: 'Tan Color',
        hex: '#D2B48C',
        images: [
          vNeckModelImg('Vneck_tan.png'),
          vNeckSideImg('Tan_scrub.png'),
          vNeckHangerImg('V_neck_Tan_color_scrub_suit.png'),
        ],
      },
    ],
    description:
      'Elegant V-neck scrub designed for healthcare professionals who want style, flexibility, and comfort during long work hours.',
    details: [
      'Stylish V-neck design for modern professional appearance',
      'Relaxed fit for easy movement and flexibility',
      'Multiple spacious pockets for daily essentials',
      'Tailored stitching for flattering feminine fit',
      'Perfect for hospitals, clinics, and labs',
    ],
    fabricDescription:
      'Crafted with premium Classic fabric that offers breathable softness, durability, and everyday comfort.',
    fabricCare: [
      '75% Poly',
      '25% Viscose',
      'Breathable lightweight fabric',
      'Machine wash cold',
      'Do not bleach',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 3,
    variant_id: 103,
    title: "ecoflex™ Lite Women's Longsleeves Scrub",
    category: 'Scrubs',
    fabric: 'Ecoflex Lite',
    color: 'Green',
    price: 1050.0,
    oldPrice: 1400.0,
    rating: 4.5,
    type: 'women',
    image: parallelImg('Dark_green_full_sleeves_zip_scrub_suit_women.png'),
    images: [
      parallelImg('Dark_green_full_sleeves_zip_scrub_suit_women.png'),
      modelImg('Dark_Green_full_sleeves.png'),
    ],
    colors: [
      {
        name: 'Green',
        hex: '#006400',
        variant_id: 103,
        images: [
          parallelImg('Dark_green_full_sleeves_zip_scrub_suit_women.png'),
          modelImg('Dark_Green_full_sleeves.png'),
        ],
      },
    ],
    description:
      'Advanced Ecoflex Lite scrub designed for lightweight comfort, flexibility, and modern professional styling.',
    details: [
      'Flexible stretchable design for active movement',
      'Breathable fabric for long shifts',
      'Stylish modern fit',
      'Functional utility pockets',
      'Comfortable lightweight feel',
    ],
    fabricDescription:
      'Made from lightweight Ecoflex Lite stretch fabric engineered for flexibility and all-day comfort.',
    fabricCare: [
      '80% Poly',
      '20% Spandex Blend',
      'Machine wash gentle cycle',
      'Do not iron on high heat',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 4,
    variant_id: 104,
    title: "Classic Women's Round-Neck Scrub",
    category: 'Scrubs',
    fabric: 'Classic',
    color: 'Soft Blue+Grey',
    price: 600.0,
    oldPrice: 800.0,
    rating: 4.5,
    type: 'women',
    image: parallelImg('Round_neck_blue+grey_scrub_suit_women.png'),
    images: [
      parallelImg('Round_neck_blue+grey_scrub_suit_women.png'),
      modelImg('Grey+blue_scrub.png'),
    ],
    colors: [
      {
        name: 'Soft Blue+Grey',
        hex: '#6699CC',
        variant_id: 104,
        images: [
          parallelImg('Round_neck_blue+grey_scrub_suit_women.png'),
          modelImg('Grey+blue_scrub.png'),
        ],
      },
    ],
    description:
      'Elegant round-neck scrub designed for healthcare professionals who want style, flexibility, and comfort during long work hours.',
    details: [
      'Stylish round-neck design for modern professional appearance',
      'Relaxed fit for easy movement and flexibility',
      'Multiple spacious pockets for daily essentials',
      'Tailored stitching for flattering feminine fit',
      'Perfect for hospitals, clinics, and labs',
    ],
    fabricDescription:
      'Crafted with premium Classic fabric that offers breathable softness, durability, and everyday comfort.',
    fabricCare: [
      '75% Poly',
      '25% Viscose',
      'Breathable lightweight fabric',
      'Machine wash cold',
      'Do not bleach',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 5,
    variant_id: 105,
    title: "Classic Women's Longsleeves Scrub",
    category: 'Scrubs',
    fabric: 'Classic',
    color: 'Yellow',
    price: 800.0,
    oldPrice: 1000.0,
    rating: 4.5,
    type: 'women',
    isBestSeller: true,
    image: parallelImg('Light_yellow_full_sleeves.png'),
    images: [
      parallelImg('Light_yellow_full_sleeves.png'),
      modelImg('light_yellow_full_sleeves_scrub.png'),
    ],
    colors: [
      {
        name: 'Yellow',
        hex: '#FFFF00',
        variant_id: 105,
        images: [
          parallelImg('Light_yellow_full_sleeves.png'),
          modelImg('light_yellow_full_sleeves_scrub.png'),
        ],
      },
      {
        name: 'Tan',
        hex: '#D2B48C',
        images: [
          parallelImg('Tan_color_full_sleeves.png'),
          modelImg('Tan_color_full_sleeves_scrub.png'),
        ],
      },
    ],
    description:
      'Classic full sleeve scrub designed for added protection and polished professional appearance.',
    details: [
      'Long sleeve design for added coverage',
      'Elegant structured stitching',
      'Comfortable breathable fit',
      'Functional storage pockets',
      'Professional hospital-ready style',
    ],
    fabricDescription:
      'Made from premium Classic fabric for breathable comfort and durability during long shifts.',
    fabricCare: ['75% Poly', '25% Viscose', 'Machine washable', 'Do not bleach', 'Low heat dry'],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 6,
    variant_id: 106,
    title: "ecoflex™ Lite Women's V-Neck Scrub",
    category: 'Scrubs',
    fabric: 'Ecoflex Lite',
    color: 'Dark Grey',
    price: 999.0,
    oldPrice: 1200.0,
    rating: 4.5,
    type: 'women',
    image: collarGirlImg('Dark_Grey1.png'),
    images: [
      collarGirlImg('Dark_Grey1.png'),
      collarGirlImg('Dark_Grey2.png'),
      collarGirlImg('Dark_grey3.png'),
    ],
    colors: [
      {
        name: 'Dark Grey',
        hex: '#A9A9A9',
        variant_id: 106,
        images: [
          collarGirlImg('Dark_Grey1.png'),
          collarGirlImg('Dark_Grey2.png'),
          collarGirlImg('Dark_grey3.png'),
        ],
      },
      {
        name: 'Black',
        hex: '#000000',
        images: [
          collarGirlImg('Blue1.png'),
          collarGirlImg('blue2.png'),
          collarGirlImg('blue3.png'),
        ],
      },
      {
        name: 'Blue',
        hex: '#0000FF',
        images: [
          collarGirlImg('Blue1.png'),
          collarGirlImg('blue2.png'),
          collarGirlImg('blue3.png'),
        ],
      },
      {
        name: 'Green',
        hex: '#006400',
        images: [
          collarGirlImg('Green1.png'),
          collarGirlImg('Green2.png'),
          collarGirlImg('Green3.png'),
        ],
      },
      {
        name: 'Brown',
        hex: '#964B00',
        images: [
          collarGirlImg('Brown1.png'),
          collarGirlImg('Brown2.png'),
          collarGirlImg('Brown3.png'),
        ],
      },
      {
        name: 'Navy Blue',
        hex: '#000080',
        images: [
          collarGirlImg('Navy_blue1.png'),
          collarGirlImg('Navy_blue2.png'),
          collarGirlImg('Navy_blue3.png'),
        ],
      },
    ],
    description:
      'Ecoflex Lite V-neck scrub made for lightweight comfort, flexibility, and modern everyday medical wear.',
    details: [
      'Stylish V-neck professional design',
      'Ultra-lightweight flexible fit',
      'Breathable fabric for active movement',
      'Functional side pockets',
      'Ideal for long hospital shifts',
    ],
    fabricDescription:
      'Made from lightweight Ecoflex Lite fabric engineered for flexibility, breathability, and comfort.',
    fabricCare: [
      '80% Poly',
      '20% Spandex Blend',
      'Stretchable lightweight material',
      'Machine wash gentle',
      'Do not iron high heat',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 7,
    variant_id: 107,
    title: "Ecoflex Women's Sleeves Scrub",
    category: 'Scrubs',
    fabric: 'Ecoflex',
    color: 'Blue',
    price: 800.0,
    oldPrice: 1100.0,
    rating: 4.5,
    type: 'women',
    image: parallelImg('Vneck_dark_blue_scrub_women.png'),
    images: [parallelImg('Vneck_dark_blue_scrub_women.png'), modelImg('Navy blue scrub.png')],
    colors: [
      {
        name: 'Blue',
        hex: '#00008B',
        variant_id: 107,
        images: [parallelImg('Vneck_dark_blue_scrub_women.png'), modelImg('Navy blue scrub.png')],
      },
    ],
    description:
      'Premium Ecoflex scrub with sleeves designed for superior flexibility and all-day working comfort.',
    details: [
      'Sleeved design for enhanced coverage',
      'Flexible 4-way stretch movement',
      'Soft breathable texture',
      'Deep utility pockets',
      'Professional sleek fit',
    ],
    fabricDescription:
      'Crafted from premium Ecoflex stretch fabric for maximum flexibility and moisture control.',
    fabricCare: [
      '80% Poly',
      '20% Spandex Blend',
      'Machine wash cold',
      'Do not bleach',
      'Hang dry recommended',
    ],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },

  {
    id: 8,
    variant_id: 108,
    title: "Classic Women's V-Neck Scrub",
    category: 'Scrubs',
    fabric: 'Classic',
    color: 'Dark Green',
    price: 850.0,
    oldPrice: 1100,
    rating: 4.5,
    type: 'women',
    image: vNeckModelImg('dark_green1.png'),
    images: [
      vNeckModelImg('dark_green1.png'),
      vNeckSideImg('dark_green2.png'),
      vNeckHangerImg('dark_green3.png'),
    ],
    colors: [
      {
        name: 'Dark Green',
        hex: '#013220',
        variant_id: 108,
        images: [
          vNeckModelImg('dark_green1.png'),
          vNeckSideImg('dark_green2.png'),
          vNeckHangerImg('dark_green3.png'),
        ],
      },
      {
        name: 'Blue',
        hex: '#00008B',
        images: [
          vNeckModelImg('vdark_blue.png'),
          vNeckSideImg('Vneck_dark_blue.png'),
          vNeckHangerImg('Dark_blue_scrub.png'),
        ],
      },
      {
        name: 'Green',
        hex: '#006400',
        images: [
          vNeckModelImg('Vneck_green.png'),
          vNeckSideImg('Vneck_green_scrub.png'),
          vNeckHangerImg('Green_medical_scrub_suit.png'),
        ],
      },
      {
        name: 'Dust Pink',
        hex: '#D58A94',
        images: [
          vNeckModelImg('Vneck_pink.png'),
          vNeckSideImg('Vneck_green_scrub.png'),
          vNeckHangerImg('Pink_scrub.png'),
        ],
      },
      {
        name: 'Mint Green',
        hex: '#98FB98',
        images: [
          vNeckModelImg('Vneck_mint_green.png'),
          vNeckSideImg('Vneck_mint_green.png'),
          vNeckHangerImg('Green_medical_scrub_suit.png'),
        ],
      },
      {
        name: 'Tan Color',
        hex: '#D2B48C',
        images: [
          vNeckModelImg('Vneck_tan.png'),
          vNeckSideImg('Tan_scrub.png'),
          vNeckHangerImg('V_neck_Tan_color_scrub_suit.png'),
        ],
      },
    ],
    description:
      'Classic V-neck scrub with modern tailoring for elegant styling and everyday hospital comfort.',
    details: [
      'Professional V-neck styling',
      'Relaxed comfortable fit',
      'Spacious storage pockets',
      'Soft breathable material',
      'Elegant tailored feminine stitching',
    ],
    fabricDescription:
      'Premium Classic fabric offers durability, softness, and breathable performance all day long.',
    fabricCare: ['75% Poly', '25% Viscose', 'Machine wash cold', 'Do not bleach', 'Dry low heat'],
    returnDescription:
      "We want you to love your scrubs. If something isn't right, you can request a return or exchange within 7 days of delivery for all non-customised orders.",
    returnPoints: [
      'Embroidery products are not eligible for return or exchange.',
      'Items that have been used, washed, or had their tags removed cannot be returned.',
      'Orders placed during sale events are final and not eligible for return but can be exchanged.',
    ],
  },
]
