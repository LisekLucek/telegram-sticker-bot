CREATE TABLE `sets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
);

CREATE TABLE `stickers` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `set_id` int(11) unsigned NOT NULL,
  `in_set_index` tinyint(1) unsigned DEFAULT NULL,
  `in_set_id` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hash` bigint(20) unsigned NOT NULL,
  `emoji` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_animated` tinyint(1) DEFAULT NULL,
  `is_video` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_stickers_set_id_idx` (`set_id`),
  KEY `hash_index` (`hash`),
  KEY `in_set_index` (`in_set_index`),
  KEY `in_set_id_index` (`in_set_id`)
);
