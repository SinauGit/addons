from odoo import api, fields, models

class SuratPesenan(models.Model):
    _name = 'surat.pesenan'
    _description = 'Data Surat Pesenan Barang'

    name = fields.Char(string='Nama Barang')
    nobarang = fields.Integer(string='No Barang')
    tanggal = fields.Datetime(string='Tanggal')
    jumlah = fields.Integer(string='Jumlah')
    ket = fields.Char(string='Keterangan')
    dokumentasi = fields.Binary(string='Dokumentasi')


class SuratPengajuan(models.Model):
    _name = 'surat.pengajuan'
    _description = 'Data Surat Pengajuan Barang'

    name = fields.Char(string='Nama Barang')
    nobarang = fields.Integer(string='No Barang')
    tanggal = fields.Datetime(string='Tanggal')
    jumlah = fields.Integer(string='Jumlah')
    ket = fields.Char(string='Keterangan')
    dokumentasi = fields.Binary(string='Dokumentasi')

class TandaTerima(models.Model):
    _name = 'tanda.terima'
    _description = 'Data Tanda Terima Barang'

    name = fields.Char(string='Nama Barang')
    nobarang = fields.Integer(string='No Barang')
    tanggal = fields.Datetime(string='Tanggal')
    jumlah = fields.Integer(string='Jumlah')
    ket = fields.Char(string='Keterangan')
    dokumentasi = fields.Binary(string='Dokumentasi')

class BukuPembelian(models.Model):
    _name = 'buku.pembelian'
    _description = 'Data Buku Pembelian Barang'

    tandaterima = fields.Datetime('Tanggal Terima')
    name = fields.Char(string='Nama dan Alamat Pengirim')
    deskripsi = fields.Char(string='Deskripsi Uraian Barang')
    jumlah = fields.Integer(string='Jumlah Barang')
    harga = fields.Integer(string='Harga Barang')
    buktipengiriman = fields.Binary(string='Bukti Pengiriman')
    ket = fields.Char(string='Keterangan')


class BukuPenerimaan(models.Model):
    _name = 'data.bukupenerimaan'
    _description = 'Data Buku Penerimaan Barang'

    tandaterima = fields.Date('Tanggal Surat Pesanan')
    name = fields.Char(string='Nama dan Alamat Rekanan')
    uraian = fields.Char(string='Uraian Barang')
    jumlah = fields.Integer(string='Jumlah Barang')
    harga = fields.Integer(string='Harga Barang')
    tanggal = fields.Date(string='Tanggal Penerimaan Barang')
    buktipembayaran = fields.Binary(string='Tanda Bukti Pembayaran')
    ket = fields.Char(string='Keterangan')

class BukuPengeluaran(models.Model):
    _name = 'data.bukupengeluaran'
    _description = 'Data Buku Pengeluaaran Barang'

    tanggal = fields.Date(string='Tanggal')
    diberikan = fields.Char(string='Diberikan Kepada')
    buktipengeluaran = fields.Date(string='Bukti Pengeluaran')
    nomor = fields.Integer(string='Nomor')
    name = fields.Char(string='Nama dan Uraian Barang')
    jumlah = fields.Integer(string='Banyaknya')
    hargasat = fields.Integer(string='Harga Satuan')
    harjum = fields.Integer(string='Harga Jumlah')
    stok = fields.Integer(string='Sisa/Stok')
    ket = fields.Char(string='Keterangan')

class KartuBarang(models.Model):
    _name = 'data.kartubarang'
    _description = 'Data Kartu Barang'

    tanggal = fields.Date(string='Tanggal')
    uraian = fields.Char(string='Uraian')
    kodebukti = fields.Char(string='Kode Bukti')
    masuk = fields.Integer(string='Masuk')
    keluar = fields.Integer(string='Keluar')
    sisa = fields.Integer(string='Sisa')
    paraf = fields.Binary(string='Paraf')