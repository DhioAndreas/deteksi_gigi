-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 25 Jul 2025 pada 09.24
-- Versi server: 10.4.27-MariaDB
-- Versi PHP: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `deteksi_penyakit_gigi`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `dataset`
--

CREATE TABLE `dataset` (
  `id` int(11) NOT NULL,
  `label` varchar(100) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `dataset`
--

INSERT INTO `dataset` (`id`, `label`, `filename`, `created_at`) VALUES
(1, 'Gigi Berlubang', 'wc43.jpg', '2025-07-17 17:31:29'),
(2, 'Gigi Berlubang', 'caries_0_7.jpeg', '2025-07-17 17:33:25'),
(3, 'Gigi Berlubang', 'caries_0_42.jpeg', '2025-07-24 19:46:29'),
(4, 'Gigi Berlubang', 'caries_0_160.jpeg', '2025-07-24 19:46:57'),
(5, 'Gigi Berlubang', 'caries_0_1158.jpeg', '2025-07-24 19:47:47'),
(6, 'Gigi Berkarang', 'kalkulus_7.jpg', '2025-07-24 19:48:15'),
(7, 'Gigi Berkarang', 'kalkulus_23.jpg', '2025-07-24 19:48:39'),
(8, 'Gigi Berkarang', 'kalkulus_15.jpg', '2025-07-24 19:48:58'),
(9, 'Gigi Berkarang', 'kalkulus_32.jpg', '2025-07-24 19:49:28'),
(10, 'Gigi Berkarang', 'kalkulus_41.jpg', '2025-07-24 19:50:03');

-- --------------------------------------------------------

--
-- Struktur dari tabel `hasil_klasifikasi`
--

CREATE TABLE `hasil_klasifikasi` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `prediksi` varchar(50) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `waktu` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `hasil_klasifikasi`
--

INSERT INTO `hasil_klasifikasi` (`id`, `nama`, `filename`, `prediksi`, `confidence`, `waktu`) VALUES
(67, 'Reza Maulana', '1001189629.jpg', 'Gigi Berlubang', 0.73103, '2025-07-07 14:10:55'),
(68, 'Erga Wanda', '1001189630.jpg', 'Gigi Berkarang', 0.73094, '2025-07-07 15:02:03'),
(70, 'Erga Wanda', '1001190355.jpg', 'Gigi Berlubang', 0.539245, '2025-07-10 06:40:26'),
(75, 'Reza Maulana', '1001190274.jpg', 'Gigi Berlubang', 0.558773, '2025-07-10 10:11:01'),
(77, 'Reza Maulana', '1001189630.jpg', 'Gigi Berkarang', 0.57603, '2025-07-10 10:16:24'),
(78, 'Reza Maulana', '1001189629.jpg', 'Gigi Berlubang', 0.576024, '2025-07-10 10:16:50'),
(83, 'Reza Maulana', '1001190355.jpg', 'Gigi Berlubang', 0.522334, '2025-07-10 10:19:36'),
(86, 'Reza Maulana', '1001189629.jpg', 'Gigi Berlubang', 0.57611, '2025-07-10 11:21:31'),
(89, 'Erga Wanda', '1001189629.jpg', 'Gigi Berlubang', 0.575756, '2025-07-10 15:44:23'),
(90, 'Erga Wanda', '1001189630.jpg', 'Gigi Berkarang', 0.576109, '2025-07-10 15:44:52'),
(95, 'Muhammad Hifdi', '1001189630.jpg', 'Gigi Berkarang', 0.576109, '2025-07-10 15:51:50'),
(96, 'Muhammad Hifdi', '1001189629.jpg', 'Gigi Berlubang', 0.575756, '2025-07-10 15:51:59'),
(100, 'Erga Wanda', '1001189630.jpg', 'Gigi Berkarang', 0.576109, '2025-07-10 16:11:24'),
(101, 'Erga Wanda', '1001189629.jpg', 'Gigi Berlubang', 0.575756, '2025-07-10 16:11:47'),
(102, 'Reza Maulana', '1001189630.jpg', 'Gigi Berkarang', 0.576109, '2025-07-11 05:30:47'),
(103, 'Reza Maulana', '1001189629.jpg', 'Gigi Berlubang', 0.575756, '2025-07-24 12:40:47');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengguna`
--

CREATE TABLE `pengguna` (
  `id_pengguna` int(11) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','user') DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pengguna`
--

INSERT INTO `pengguna` (`id_pengguna`, `nama`, `email`, `password`, `role`) VALUES
(1, 'Amrulah', 'amrulah@gmail.com', 'scrypt:32768:8:1$62O8yQyjMMAbNrUA$146a07d55763004630b56e48c59b49cc700f747d0b2f083c7803e8fbeee6208713ba8b4f0e2c647f230a2d7315fc4bce7a8f4316fe13cc18cb68972a2ccb2919', 'user'),
(3, 'Admin', 'admin@gmail.com', 'scrypt:32768:8:1$3pkvwpfCpdn8QRhZ$f125f3c333995e10832c077e1815bc8120c6b2a4fda3c9509ca41be8b1c21b7ba4b3c1c58c8b5e4b6aa9137fb997e764554807f6dd58f9f37d546f342d783956', 'admin'),
(4, 'Erga Wanda', 'erga@gmail.com', 'scrypt:32768:8:1$cSOtYNeN2Q3d4qbD$af0b4dfa1151d633ec6db21a10df363ac4effa5084831f6495b4a4db139f28e7e656dd2ac4a7c068ce7c317018d954944ee96a8aa0ecd650e8a12313d25c2309', 'user'),
(5, 'Reza Maulana', 'reza@gmail.com', 'scrypt:32768:8:1$XQ1ts4E7yC4lKFjD$d03ac925cdd587b72c6ea8d64d47600321040a602930d15e05b580d671b6dc6e289bfdd37b6b6b3dd6076b70d66526bdf8ba2a87768d3c82168479c76744677d', 'user'),
(6, 'Wisnu Anggoro', 'wiznew24@gmail.com', 'scrypt:32768:8:1$b6U0ojTHKVHpMGKX$ea44c30b7ba0f79a357b137e41a633d3de48bd026ee9dee87add0ed6d93bdaa272c82e6b8ac39c977f76f7b4844d45fb82a72e8cc5cc9ef3223fe12aed7ee5ce', 'user'),
(7, 'Nazar Hafiz', 'nazar@gmail.com', 'scrypt:32768:8:1$qwVWBK7xnDgp1YnZ$9dd738acf4f1d1348e76254f51f3b5c64a0b6a466f8f1a5b7fb70bae8565863b52583634dc65f6a540cd3ddde56556543eed8c3a0ba13a7c502b876fce678e82', 'user'),
(8, 'Rafli Pratama', 'rafli@gmail.com', 'scrypt:32768:8:1$7dMrdVe1foK8HrIV$23dea8ee2d83eafe51aac0210f940fef414add9ad5281979f2b0f3696c73b26e752d18fa08c604dd5a1e1c50134cbb811da7d590b6cbea42b57bc874f6431a3d', 'user'),
(9, 'Muhammad Hifdi', 'hifdi@gmail.com', 'scrypt:32768:8:1$vOhlkTHD1rALY0th$61cfa14854267e4e99a252ca5d182332da9add4fe886ae8544c615087a4f390947805cee331499f51ba117dc660406cdc519051e277bd58b8125eb06809c70e0', 'user'),
(10, 'Risky ardi', 'deki@gmail.com', 'scrypt:32768:8:1$JFhUwJp07csQKCSo$455bfe6eb83b52a1fe1d397f621d3bff9cc79002010d6bafad73eae2fc52d2c2d4538e4244afdafd718a04255b861a8190b8044b0539b963cbc688a90951deee', 'user'),
(11, 'Taufik hidayat', 'erilpakaya17@gmail.com', 'scrypt:32768:8:1$0DSYxmvAOQuDWXpa$7de8954c59eec23a296f3fd38c68454f39fcb2002c8f12ab07b0c933bc785995094dfb6139d996fed77dce4172a8ee9dc3bf9d098bc28b42bbee379cd92c74b9', 'user');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `dataset`
--
ALTER TABLE `dataset`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `hasil_klasifikasi`
--
ALTER TABLE `hasil_klasifikasi`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  ADD PRIMARY KEY (`id_pengguna`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `dataset`
--
ALTER TABLE `dataset`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `hasil_klasifikasi`
--
ALTER TABLE `hasil_klasifikasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=104;

--
-- AUTO_INCREMENT untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
