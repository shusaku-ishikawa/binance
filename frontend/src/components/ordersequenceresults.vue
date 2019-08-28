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
        <tr v-for="(osr, index) in data" :key="index">
          <td align="center">{{ osr.t1_result.order_id }}</td>
          <td align="center">{{ osr.t1_result.str_symbol }}/{{ osr.t1_result.side }}</td>
          <td align="center">{{ osr.t1_result.expected_rate }}</td>
          <td align="center">{{ osr.t1_result.actual_rate }}</td>
          <td align="center">{{ osr.t2_result.order_id }}</td>
          <td align="center">{{ osr.t2_result.str_symbol }}/{{ osr.t1_result.side }}</td>
          <td align="center">{{ osr.t2_result.expected_rate }}</td>
          <td align="center">{{ osr.t2_result.actual_rate }}</td>
          <td align="center">{{ osr.t3_result.order_id }}</td>
          <td align="center">{{ osr.t3_result.str_symbol }}/{{ osr.t1_result.side }}</td>
          <td align="center">{{ osr.t3_result.expected_rate }}</td>
          <td align="center">{{ osr.t3_result.actual_rate }}</td>
          <td align="center">{{ osr.expected_profit }}</td>
          <td align="center">{{ osr.profit }}</td>
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
        { text: '#1 orderId' },
        { text: '#1 注文' },
        { text: '#1 想定価格' },
        { text: '#1 実価格' },
        { text: '#2 orderId' },
        { text: '#2 注文' },
        { text: '#2 想定価格' },
        { text: '#2 実価格' },
        { text: '#3 orderId' },
        { text: '#3 注文' },
        { text: '#3 想定価格' },
        { text: '#3 実価格' },
        { text: '想定利益' },
        { text: '利益' }
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
  async created () {
    this.fetchData(this.page)
  },
  watch: {
    // on page change
    page: function (page) {
      this.fetchData(page)
    }
  },
  methods: {
    async fetchData (page) {
      this.loading = true
      let pagedUrl = 'ordersequenceresults?page=' + page
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
