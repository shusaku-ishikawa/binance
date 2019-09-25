<template>
  <v-layout>
    <v-flex
      md12
      xs12
    >
      <div
        v-show="loading" class="loader">Now loading...</div>
      <div
        class="table-wrapper"
        v-show='!loading && hasData'
      >
        <table>
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
              <td align="center">{{ o.quantity | toFixed }}</td>
              <td align="center">{{ o.quote_quantity | toFixed }}</td>
              <td align="center">{{ o.price | toFixed }}</td>
              <td align="center">{{ o.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p
        v-show="!loading && !hasData"
        class="no_data"
      >
        レコードが存在しません
      </p>
      <v-pagination
        v-model="pagination.page"
        v-show="!loading && hasData"
        :circle="pagination.circle"
        :disabled="pagination.disabled"
        :length="pagination.length"
        :next-icon="pagination.nextIcon"
        :prev-icon="pagination.prevIcon"
        :page="pagination.page"
        :total-visible="pagination.totalVisible"
      ></v-pagination>
    </v-flex>
  </v-layout>
</template>
<style scoped>
  div.table-wrapper {
    width: 100%;
    overflow: scroll;
  }
  table {
    overflow: scroll;
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
  p.no_data {
    color: red
  }
</style>
  
<script>
export default {
  data () {
    return {
      loading: false,
      headers: [
        { text: 'orderId' },
        { text: 'Time' },
        { text: 'Symbol' },
        { text: 'Side' },
        { text: 'baseQty' },
        { text: 'quoteQty' },
        { text: 'Price' },
        { text: 'Status' }
      ],
      data: [],
      pagination: {
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
    }
  },
  computed: {
    hasData: function () {
      return this.data.length > 0
    }
  },
  watch: {
    // on page change
    page: function (page) {
      this.fetchData(page)
    }
  },
  async created () {
    this.fetchData(this.pagination.page)
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
        this.pagination.length = result.data.page_count
        this.data = result.data.result
      } catch (err) {
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
      this.loading = false
    }
  },
  filters: {
    toFixed: function (val) {
      const precistion = 1000000
      if (isNaN(val)) {
        return 0
      }
      return parseInt(val * precistion) / precistion
    }
  }
}
</script>
