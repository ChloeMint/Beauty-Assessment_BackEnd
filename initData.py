from database import *

with app.app_context():
    # 管理员账号
    user = User(phone="15715815825", permissions=0)
    user.set_password("12345678910")

    # 普通账号
    user2 = User(phone="12345678910")
    user2.set_password("12345678910")

    db.session.add_all([user, user2])
    db.session.commit()

    product = Product(
        type="makeUp",
        product_name="卡姿兰唇釉",
        start_time="2024.3.19",
        end_time="2024.4.19",
        user_id=1,
        product_introduce="体验细腻柔软的柔滑慕斯质地，让唇部轻盈柔软，叠加涂抹，让唇色更加饱满丰盈。 甄选蜂蜜提取物、野生芒果（IRVINGIA GABONENSIS）果仁脂和芝麻（SESAMUM "
                          "INDICUM）籽提取物令唇部在上妆的同时持续保持滋润感",
        status=1,
        audit_by=1
    )
    product.add_image("/image/1/卡姿兰唇釉.jpg")
    product.add_image("/image/1/卡姿兰唇釉.jpg")
    product.add_skin_type("油性皮")
    product.add_skin_type("干性皮")
    product.add_skin_type("混合皮")
    product.add_skin_type("敏感皮")
    product.add_skin_type("中性皮")

    product2 = Product(
        type="makeUp",
        product_name="卡姿兰唇釉2",
        start_time="2024.4.19",
        end_time="2024.5.19",
        user_id=2,
        product_introduce="体验细腻柔软的柔滑慕斯质地，让唇部轻盈柔软，叠加涂抹，让唇色更加饱满丰盈。 甄选蜂蜜提取物、野生芒果（IRVINGIA GABONENSIS）果仁脂和芝麻（SESAMUM "
                          "INDICUM）籽提取物令唇部在上妆的同时持续保持滋润感",
        status=1,
        audit_by=1

    )
    product2.add_image("/image/2/卡姿兰唇釉.jpg")
    product2.add_image("/image/2/卡姿兰唇釉.jpg")
    product2.add_skin_type("油性皮")
    product2.add_skin_type("干性皮")
    product2.add_skin_type("混合皮")
    product2.add_skin_type("敏感皮")
    product2.add_skin_type("中性皮")

    product3 = Product(
        type="clean",
        product_name="半亩花田氨基酸洗面奶",
        start_time="2024.4.19",
        end_time="2024.5.19",
        user_id=1,
        product_introduce="半亩花田氨基酸洗面奶含有进口氨基酸成分，使用起来温和不刺激，细密泡沫可以深入毛孔，带走肌肤深层油脂污垢，对肌肤进行深层清洁，还添加了苦参提取物，清洁除螨，有效改善痘痘与闭口，还有神经酰胺3，洗后使得肌肤水润不紧绷。",
        status=1,
        audit_by=1

    )
    product3.add_image("/image/1/半亩花田.jpg")
    product3.add_image("/image/1/半亩花田.jpg")
    product3.add_skin_type("油性皮")
    product3.add_skin_type("干性皮")
    product3.add_skin_type("混合皮")
    product3.add_skin_type("敏感皮")
    product3.add_skin_type("中性皮")

    product4 = Product(
        type="clean",
        product_name="半亩花田氨基酸洗面奶",
        start_time="2024.5.19",
        end_time="2024.6.19",
        user_id=2,
        product_introduce="半亩花田氨基酸洗面奶含有进口氨基酸成分，使用起来温和不刺激，细密泡沫可以深入毛孔，带走肌肤深层油脂污垢，对肌肤进行深层清洁，还添加了苦参提取物，清洁除螨，有效改善痘痘与闭口，还有神经酰胺3，洗后使得肌肤水润不紧绷。",
        status=1,
        audit_by=1

    )
    product4.add_image("/image/2/半亩花田.jpg")
    product4.add_image("/image/2/半亩花田.jpg")
    product4.add_skin_type("油性皮")
    product4.add_skin_type("干性皮")
    product4.add_skin_type("混合皮")
    product4.add_skin_type("敏感皮")
    product4.add_skin_type("中性皮")

    product5 = Product(
        type="care",
        product_name="蜂花护发素",
        start_time="2024.5.19",
        end_time="2024.6.19",
        user_id=1,
        product_introduce="蜂花护发素自1985年以来，以匠心品质和亲民姿态书写中国护发史。其标志性瓶身与香氛唤起温暖记忆，成为一代代人心中的家的味道。蜂花结合自然花卉与现代科技，提供高效修护与滋养，以超高性价比赢得市场青睐。品牌紧跟市场需求，推出新品，注重环保与品质，传递怀旧与关怀。选择蜂花，即选择简约生活与纯粹护发享受，重拾温暖记忆",
        status=1,
        audit_by=1

    )

    product5.add_image("/image/1/蜂花护发素.jpg")
    product5.add_image("/image/1/蜂花护发素.jpg")
    product5.add_skin_type("油性皮")
    product5.add_skin_type("干性皮")
    product5.add_skin_type("混合皮")
    product5.add_skin_type("敏感皮")
    product5.add_skin_type("中性皮")

    product6 = Product(
        type="care",
        product_name="蜂花护发素",
        start_time="2024.6.19",
        end_time="2024.7.19",
        user_id=2,
        product_introduce="蜂花护发素自1985年以来，以匠心品质和亲民姿态书写中国护发史。其标志性瓶身与香氛唤起温暖记忆，成为一代代人心中的家的味道。蜂花结合自然花卉与现代科技，提供高效修护与滋养，以超高性价比赢得市场青睐。品牌紧跟市场需求，推出新品，注重环保与品质，传递怀旧与关怀。选择蜂花，即选择简约生活与纯粹护发享受，重拾温暖记忆",
        status=1,
        audit_by=1

    )
    product6.add_image("/image/2/蜂花护发素.jpg")
    product6.add_image("/image/2/蜂花护发素.jpg")
    product6.add_skin_type("油性皮")
    product6.add_skin_type("干性皮")
    product6.add_skin_type("混合皮")
    product6.add_skin_type("敏感皮")
    product6.add_skin_type("中性皮")

    product7 = Product(
        type="care",
        product_name="蜂花护发素",
        start_time="2024.6.19",
        end_time="2024.7.19",
        user_id=2,
        product_introduce="蜂花护发素自1985年以来，以匠心品质和亲民姿态书写中国护发史。其标志性瓶身与香氛唤起温暖记忆，成为一代代人心中的家的味道。蜂花结合自然花卉与现代科技，提供高效修护与滋养，以超高性价比赢得市场青睐。品牌紧跟市场需求，推出新品，注重环保与品质，传递怀旧与关怀。选择蜂花，即选择简约生活与纯粹护发享受，重拾温暖记忆",
        status=0,
        audit_by=1

    )
    product7.add_image("/image/2/蜂花护发素.jpg")
    product7.add_image("/image/2/蜂花护发素.jpg")
    product7.add_skin_type("油性皮")
    product7.add_skin_type("干性皮")

    product8 = Product(
        type="care",
        product_name="蜂花护发素",
        start_time="2024.6.19",
        end_time="2025.7.19",
        user_id=2,
        product_introduce="蜂花护发素自1985年以来，以匠心品质和亲民姿态书写中国护发史。其标志性瓶身与香氛唤起温暖记忆，成为一代代人心中的家的味道。蜂花结合自然花卉与现代科技，提供高效修护与滋养，以超高性价比赢得市场青睐。品牌紧跟市场需求，推出新品，注重环保与品质，传递怀旧与关怀。选择蜂花，即选择简约生活与纯粹护发享受，重拾温暖记忆",
        status=3,
        audit_by=1

    )
    product8.add_image("/image/2/蜂花护发素.jpg")
    product8.add_image("/image/2/蜂花护发素.jpg")
    product8.add_skin_type("油性皮")
    product8.add_skin_type("干性皮")

    db.session.add_all([product, product2, product3, product4, product5, product6, product7, product8])
    db.session.commit()

    joined_test = JoinedTest(user_id=1, product_id=2)
    db.session.add(joined_test)
    db.session.commit()

    test = Test(product_id=1, skin_type="干性皮", tag="丝滑", score=5, feeling="feeling", user_id=1)
    test.add_image("/image/1/蜂花护发素.jpg")
    db.session.add(test)
    db.session.commit()

    userComment = UserComment(product_id=1, user_id=1, comment_text="comment_text1")
    db.session.add(userComment)
    db.session.commit()
