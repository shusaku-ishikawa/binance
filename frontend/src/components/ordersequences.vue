<template>
  <v-layout>
    <v-flex
      md12
      xs12
    >
        <div v-show="loading" class="loader">Now loading...</div>
        <div v-show="processing" class="processing">Now Proessing...</div>
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
              <tr v-for="(os, index) in data" :key="index">
                <td align="center">{{ os.transition }}</td>
                <td align="center">{{ os.t1_symbol }}</td>
                <td align="center">{{ os.t1_side }}</td>
                <td align="center">{{ os.t2_symbol }}</td>
                <td align="center">{{ os.t2_side }}</td>
                <td align="center">{{ os.t3_symbol }}</td>
                <td align="center">{{ os.t3_side }}</td>
                <td align="center">
                  <v-btn
                    v-bind:disabled="processing"
                    color="teal"
                    :small=true
                    @click="showScenario(os)"
                  >
                    表示
                  </v-btn>
                  <v-btn
                    v-bind:disabled="processing"
                    color="red"
                    :small=true
                    @click="executeScenario(os)"
                  >
                    実行
                  </v-btn>
                </td>
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
    color: white;
    width: 100%;
    border: none;
    border-collapse:collapse;
    font-size: 12px;
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
  div.processing {
    position: absolute;
    top: 50%;
    left: 50%;
    opacity: 0.4
  }
  p.no_data {
    color:red
  }
</style>
<script>
export default {
  data () {
    return {
      headers: [
        { text: '通貨' },
        { text: '#1 symbol' },
        { text: '#1 side' },
        { text: '#2 symbol' },
        { text: '#2 side' },
        { text: '#3 symbol' },
        { text: '#3 side' },
        { text: '予想' }
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
      },
      loading: true,
      processing: false
    }
  },
  async created () {
    this.fetchData(this.pagination.page)
  },
  watch: {
    // on page change
    page: function (page) {
      this.laoding = true
      this.fetchData(page)
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
      this.loading = true
      let pagedUrl = 'ordersequences?page=' + page
      try {
        let result = await this.$store.dispatch(
          'http/get',
          { url: pagedUrl },
          { root: true }
        )
        console.log(result.data.result)
        this.pagination.length = result.data.page_count
        this.data = result.data.result
      } catch (err) {
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
      this.loading = false
    },
    async showScenario (item) {
      this.processing = true
      let url = 'ordersequences/' + item.id
      try {
        let result = await this.$store.dispatch(
          'http/get',
          { url: url },
          { root: true }
        )
        if (result.data) {
          let data = result.data
          if (data.is_valid) {
            var msg = data.t1_info.symbol + 'を'
            msg += data.t1_info.quantity + '分' + data.t1_info.side + 'し、'
            msg += data.t1_info.currency_acquired + 'を' + data.t1_info.amount_acquired + '取得する。'
            msg += '次に、'
            msg += data.t2_info.symbol + 'を'
            msg += data.t2_info.quantity + '分' + data.t2_info.side + 'し、'
            msg += data.t2_info.currency_acquired + 'を' + data.t2_info.amount_acquired + '取得する。'
            msg += '次に、'
            msg += data.t3_info.symbol + 'を'
            msg += data.t3_info.quantity + '分' + data.t3_info.side + 'し、'
            msg += data.t3_info.currency_acquired + 'を' + data.t3_info.amount_acquired + '取得する。'
            msg += 'この取引により、' + data.profit + '%利益がでる。'
            alert(msg)
          } else {
            alert(data.error)
          }
        }
      } catch (err) {
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
      this.processing = false
    },
    async executeScenario (item) {
      this.processing = true
      let url = 'ordersequenceresults/'
      try {
        let result = await this.$store.dispatch(
          'http/post',
          { url: url, data: { orderseq_id: item.id } },
          { root: true }
        )
        if (result.data) {
          if (result.data.error) {
            this.flash(result.data.error, 'error', {
              timeout: 1500
            })
          } else {
            console.log(result.data)
            alert(result.data.profit + '%利益がでました。')
          }
        }
      } catch (err) {
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
      this.processing = false
    }
  }
}
</script>
