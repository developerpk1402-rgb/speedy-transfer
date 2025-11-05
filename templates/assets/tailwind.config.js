/** @type {import('tailwindcss').Config} */

import daisyui from "daisyui"
import animations from '@midudev/tailwind-animations'
import theme from "@midudev/tailwind-animations/src/theme"

module.exports = {
  content: ['../../templates/speedy_app/**/*.html'],
  theme: {
    extend: {
      fontFamily: {
        'title': ["system-ui", "sans-serif"],
        'text': ['"Roboto"', "system-ui", "sans-serif"],
      }
    },
  },
  plugins: [daisyui, animations, theme, require('@tailwindcss/forms')],
  daisyui: {
    themes: ['light', 'dark',],
  }
}