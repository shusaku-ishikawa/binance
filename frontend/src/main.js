// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'

import '@mdi/font/css/materialdesignicons.css' // Ensure you are using css-loader
import Vuetify from 'vuetify'
import VueFlashMessage from 'vue-flash-message'

Vue.config.productionTip = false
require('vue-flash-message/dist/vue-flash-message.min.css')
Vue.use(VueFlashMessage)
Vue.use(Vuetify)

const opts = {
  theme: {
    dark: true
  },
  icons: {
    iconfont: 'mdi' // default - only for display purposes
  }
}

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  vuetify: new Vuetify(opts),
  components: { App },
  template: '<App/>'
})
