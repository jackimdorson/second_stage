-- DATEデータ型は、YYYY-MM-DD形式の日付を保存するために設計されており、範囲は1000-01-01から9999-12-31まで
-- cart_itemsからuser_idを切り離しても実質cartのidとuser_idは同じことをしているので同じく重複が発生する。パフォーマンスが悪くなるので切り離さない方が良い。

CREATE TABLE `cart_items` (
    `id` INT AUTO_INCREMENT,
    `date` DATE NOT NULL,
    `time` VARCHAR(20) NOT NULL,
    `price` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `attraction_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);