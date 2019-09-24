<template>
  <v-toolbar
    dense
  >
    <v-toolbar-title>BiArb</v-toolbar-title>  
    <v-spacer></v-spacer>
    <v-toolbar-items
      class="hidden-sm-and-down"
    >
      <v-btn
        v-for="item in menu"
        :key="item.icon"
        :to="item.link"
        text
      >{{ item.title }}</v-btn>
    </v-toolbar-items>
    <div
      class="hidden-md-and-up"
    >
      <v-menu
      >
        <template v-slot:activator="{ on }">
          <v-btn
            text
            v-on="on"
          >
            <v-icon>menu</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="(item, index) in menu"
            :key="index"
          >
            <v-list-item-title
              v-on:click="route(item.link)"
            >{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </v-toolbar>
</template>
<script>
export default {
  data () {
    return {
      menu: [
        { icon: 'info', title: '設定', link: 'info' },
        { icon: 'orders', title: '注文一覧', link: 'orders' },
        { icon: 'ordersequenceresults', title: '利益', link: 'ordersequenceresults' },
        { icon: 'ordersequences', title: 'シナリオ', link: 'ordersequences' },
        { icon: 'balance', title: '資産', link: 'balance' }  
      ]
    }
  },
  methods: {
    menuItems () {
      return this.menu
    },
    route (link) {
      this.$router.push(link)
    }
  }
}
</script>
