<template>
  <div align="center" class="wrapper">
    <div v-show="loading" class="loader">Now loading...</div>
    <table
      v-show='!loading'
    >
      <thead>
        <tr>
          <th v-for="(header, index) in headers" :key="index">{{ header.text }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(o, index) in data" :key="index">
          <td align="center">{{ o.order_id }}</td>
          <td align="center">{{ o.time }}</td>
          <td align="center">{{ o.str_symbol }}</td>
          <td align="center">{{ o.side }}</td>
          <td align="center">{{ o.quantity }}</td>
          <td align="center">{{ o.quote_quantity }}</td>
          <td align="center">{{ o.expected_rate }}</td>
          <td align="center">{{ o.actual_rate }}</td>
        </tr>
      </tbody>
    </table>
    <v-pagination
      v-model="page"
      v-show="!loading"
      :circle="circle"
      :disabled="disabled"
      :length="length"
      :next-icon="nextIcon"
      :prev-icon="prevIcon"
      :page="page"
      :total-visible="totalVisible"
    ></v-pagination>
  </div>
</template>
<style scoped>
  table {
    font-size: 12px;
    color: white;
    width: 100%;
    border: none;
    border-collapse:collapse
  }
  thead tr {
    border-bottom: groove #444444 1px
  }
  tbody tr {
    border-bottom: groove darkgray 1px;
  }
  tbody tr:hover {
    background-color: #555555
  }
  div.wrapper {
    align-items: center
  }
</style>

<script>
export default {
  data () {
    return {
      loading: false,
      headers: [
        { text: 'orderId' },
        { text: '時間' },
        { text: 'シンボル' },
        { text: 'side' },
        { text: 'base数量' },
        { text: 'quote数量' },
        { text: '想定価格' },
        { text: '実価格' }
      ],
      data: [],
      circle: false,
      disabled: false,
      length: 10,
      nextIcon: 'navigate_next',
      nextIcons: ['navigate_next', 'arrow_forward', 'arrow_right', 'chevron_right'],
      prevIcon: 'navigate_before',
      prevIcons: ['navigate_before', 'arrow_back', 'arrow_left', 'chevron_left'],
      page: 1,
      totalVisible: 10
    }
  },
  watch: {
    // on page change
    page: function (page) {
      this.fetchData(page)
    }
  },
  async created () {
    this.fetchData(this.page)
  },
  methods: {
    async fetchData (page) {
      let pagedUrl = 'orders?page=' + page
      this.loading = true
      try {
        let result = await this.$store.dispatch(
          'http/get',
          { url: pagedUrl },
          { root: true }
        )
        this.length = result.data.page_count
        this.data = result.data.result
      } catch (err) {
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
      this.loading = false
    }
  }
}
</script>
