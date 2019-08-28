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
        <tr v-for="(asset, index) in data" :key="index">
          <td align="center">{{ asset.asset }}</td>
          <td align="center">{{ asset.free }}</td>
          <td align="center">{{ asset.locked }}</td>
        </tr>
      </tbody>
    </table>
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
      headers: [
        { text: '通貨', value: 'asset' },
        { text: 'FREE', value: 'free' },
        { text: 'LOCKED', value: 'locked' }
      ],
      data: []
    }
  },
  async created () {
    this.loading = true
    try {
      let result = await this.$store.dispatch(
        'http/get',
        { url: 'balance' },
        { root: true }
      )
      this.data = result.data
    } catch (err) {
      this.flash(err, 'error', {
        timeout: 1500
      })
    }
    this.loading = false
  }
}
</script>
