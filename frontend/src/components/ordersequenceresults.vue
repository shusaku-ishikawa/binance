<template>
  <v-layout>
    <v-flex
      md12
      xs12
    >
      <div v-show="loading" class="loader">Now loading...</div>
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
            <tr v-for="(osr, index) in data" :key="index">
              <td align="center" v-bind:class="osr.t1_result.status">{{ osr.id }}</td>
              <td align="center" v-bind:class="osr.t1_result.status">{{ osr.t1_result.order_id }}</td>
              <td align="center" v-bind:class="osr.t1_result.status">{{ osr.t1_result.str_symbol }}/{{ osr.t1_result.side }}</td>
              <td align="center" v-bind:class="osr.t1_result.status">{{ osr.t1_result.price }}</td>
              <td align="center" v-bind:class="osr.t1_result.status">{{ osr.t1_result.status }}</td>
              <td align="center" v-bind:class="osr.t2_result.status">{{ osr.t2_result.order_id }}</td>
              <td align="center" v-bind:class="osr.t2_result.status">{{ osr.t2_result.str_symbol }}/{{ osr.t1_result.side }}</td>
              <td align="center" v-bind:class="osr.t2_result.status">{{ osr.t2_result.price }}</td>
              <td align="center" v-bind:class="osr.t2_result.status">{{ osr.t2_result.status }}</td>
              <td align="center" v-bind:class="osr.t3_result.status">{{ osr.t3_result.order_id }}</td>
              <td align="center" v-bind:class="osr.t3_result.status">{{ osr.t3_result.str_symbol }}/{{ osr.t1_result.side }}</td>
              <td align="center" v-bind:class="osr.t3_result.status">{{ osr.t3_result.price }}</td>
              <td align="center" v-bind:class="osr.t3_result.status">{{ osr.t3_result.status }}</td>
              <td align="center" v-bind:class="{ completed: osr.is_completed }">{{ osr.profit }}</td>
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
  td {
    padding: 3px 5px
  }
  tbody tr:hover {
    background-color: #555555
  }
  p.no_data {
    color:red
  }
  td.NEW {
    background-color: orangered;
  }
  td.CANCELED {
    background-color: #222222;
    color: gray
  }
  td.FILLED {
    background-color:teal;
  }
  td.PARTIALLY_FILLED {
    background-color:lightsteelblue;
  }
  td.completed {
    background-color: teal
  }
  
  
</style>
<script>
export default {
  data () {
    return {
      intervalId: '',
      loading: false,
      headers: [
        { text: 'id' },
        { text: '#1 orderId' },
        { text: '#1 Symbol' },
        { text: '#1 Price' },
        { text: '#1 Status' },
        { text: '#2 orderId' },
        { text: '#2 Symbol' },
        { text: '#2 Price' },
        { text: '#2 Status' },
        { text: '#3 orderId' },
        { text: '#3 Symbol' },
        { text: '#3 Price' },
        { text: '#3 Status' },
        { text: 'Profit' }
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
  async mounted () {
    this.loading = true
    let vueinstance = this
    await vueinstance.fetchData(vueinstance.pagination.page)
    vueinstance.intervalId = setInterval(function () {
      vueinstance.fetchData(vueinstance.pagination.page)
    }, 3000)
    this.loading = false
  },
  beforeDestroy () {
    clearInterval(this.intervalId)
  },
  watch: {
    page: async function (page) {
      this.loading = true
      await this.fetchData(page)
      this.loading = false
    }
  },
  computed: {
    hasData: function () {
      return this.data.length > 0
    }
  },
  methods: {
    async fetchData (page) {
      let pagedUrl = 'ordersequenceresults?page=' + page
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
    }
  }
}
</script>
