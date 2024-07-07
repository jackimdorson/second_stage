CREATE TABLE `order_items` (
    `id` INT AUTO_INCREMENT,
    `quantity` INT NOT NULL DEFAULT 1,
    `original_price` INT NOT NULL,
    `date` DATE NOT NULL,
    `time` VARCHAR(20) NOT NULL,
    `attraction_id` INT NOT NULL,
    `order_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`attraction_id`) REFERENCES `attractions` (`id`) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE `orders` (
    `id` INT AUTO_INCREMENT,
    `payment_status` INT NOT NULL DEFAULT 0,
    `final_price` INT NOT NULL,
    `order_number` INT NOT NULL UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
);

ALTER TABLE `orders`
MODIFY COLUMN `order_number` BIGINT NOT NULL UNIQUE;

-- 注文時にのみ電話番号が必要な場合は、注文テーブルに追加する方が適切。usersに追加すると多くのnullが生じる。
-- VARCHARにするのは--に対応するため.default00000は後から追加する際に、not nullでエラーにならないようにするため
ALTER TABLE `orders`
ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT '0000-000-000';