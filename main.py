import ast
import io
import os
from collections import Counter
from datetime import timedelta

import qrcode
from flask import Response
from flask import send_from_directory, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import desc
from apscheduler.schedulers.background import BackgroundScheduler
from database import *

app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 配置jwt加密密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=5)  # 配置token过期时间
app.secret_key = "meaning"  # 配置session密钥
jwt = JWTManager(app)
app.config['UPLOAD_FOLDER'] = 'image'  # 配置上传文件的文件夹,只有这样的相对路径可以识别
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def create_list_response(status, msg, code=200, data=[]):  # 封装响应信息
    response = {
        "status": status,
        "code": code,
        "msg": msg,
        "data": data,
        "count": len(data)
    }
    return response


def create_simple_response(status, msg, code=200, data=None):  # 封装响应信息
    response = {
        "status": status,
        "code": code,
        "msg": msg,
        "data": data,
    }
    return response


def get_pagination_info(page, pages, total, per_page):
    return {
        'current_page': page,
        'total_pages': pages,
        'total_items': total,
        'per_page': per_page
    }


# 从 user 对象中提取出 ID，这个 ID 将被用作 JWT 的 sub 声明。这样，在后续的请求中，服务器可以通过这个 sub 声明来识别是哪个用户发送的请求。
@jwt.user_identity_loader  # 登录时的access_token = create_access_token(identity=users[0]) ，会将identify传递给该方法，由它的返回值生成token
def load_user(user):
    return user.id


@app.route("/image/<path:avatar_file>")  # 查看图片的接口
def get_avatar(avatar_file):
    return send_from_directory("image", avatar_file)


@app.route("/image/<path:user_id>/<path:avatar_file>")  # 优化后查看图片的接口
def get_user_avatar(user_id, avatar_file):
    return send_from_directory("image/" + user_id + "/", avatar_file)


@app.route("/user/login", methods=["POST"])
def login():
    try:
        if "phone" not in request.json:
            return jsonify(create_simple_response("failed", "缺少手机号参数", 400))
        if "password" not in request.json:
            return jsonify(create_simple_response("failed", "缺少密码参数", 400))
        phone = request.json["phone"]
        password = request.json["password"]
        if phone == "":
            return jsonify(create_simple_response("failed", "手机号为空", 400))
        if password == "":
            return jsonify(create_simple_response("failed", "密码为空", 400))
        user = db.session.query(User).filter(User.phone == phone).first()
        if user is None:
            return jsonify(create_simple_response("failed", "该账号不存在", 400))
        if user.check_password(password):
            if user.is_delete:
                return jsonify(create_simple_response("failed", "该账号已注销,7天内可恢复", 400))
            access_token = create_access_token(identity=user)  # Authorization : Bearer <Token>
            return jsonify(
                create_simple_response("success", "登录成功", data="Bearer " + access_token))  # JWT的token认证格式)
        else:
            return jsonify(create_simple_response("failed", "输入密码错误", 400))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/user/register", methods=["POST"])
def register():
    try:
        if "phone" not in request.json:
            return jsonify(create_simple_response("failed", "缺少手机号参数", 400))
        if "password" not in request.json:
            return jsonify(create_simple_response("failed", "缺少密码参数", 400))
        phone = request.json["phone"]
        password = request.json["password"]
        if phone == "":
            return jsonify(create_simple_response("failed", "手机号为空", 400))
        if password == "":
            return jsonify(create_simple_response("failed", "密码为空", 400))
        if len(phone) != 11:
            return jsonify(create_simple_response("failed", "手机号格式错误", 400))
        user_list = db.session.query(User).filter(User.phone == phone).all()
        if len(user_list) != 0:
            return jsonify(create_simple_response("failed", "该账号已存在", 400))
        else:
            user = User(phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            if not os.path.exists(app.config['UPLOAD_FOLDER'] + "/" + str(user.id)):
                os.makedirs(app.config['UPLOAD_FOLDER'] + "/" + str(user.id))
            return jsonify(create_simple_response("success", "注册成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/user/forgetPassword", methods=["POST"])
def forget_password():
    try:
        if "phone" not in request.json:
            return jsonify(create_simple_response("failed", "缺少手机号参数", 400))
        if "password" not in request.json:
            return jsonify(create_simple_response("failed", "缺少密码参数", 400))
        phone = request.json["phone"]
        password = request.json["password"]
        if phone == "":
            return jsonify(create_simple_response("failed", "手机号为空", 400))
        if password == "":
            return jsonify(create_simple_response("failed", "密码为空", 400))
        user = db.session.query(User).filter(User.phone == phone).first()
        if user is None:
            return jsonify(create_simple_response("failed", "该账号不存在", 400))
        else:
            user.set_password(password)
            db.session.commit()
            return jsonify(create_simple_response("success", "修改密码成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/user/logout", methods=["POST", "PUT"])
@jwt_required()
def logout():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == current_user_id).first()
        if user is None:
            return jsonify(create_simple_response("failed", "该账号不存在", 400))
        user.is_delete = 1
        db.session.commit()
        return jsonify(create_simple_response("success", "注销账号成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/user/getUserInfo")
@jwt_required()
def getUserInfo():
    current_user_id = get_jwt_identity()
    user = db.session.query(User).filter(User.id == current_user_id).first()
    if user is None:
        return jsonify(create_simple_response("failed", "该用户不存在", 400))
    return jsonify(create_simple_response("success", "获取用户数据成功", data=user.to_dict()))


@app.route("/user/changeUserAvatar", methods=["POST"])
@jwt_required()
def changeAvatar():
    current_user_id = get_jwt_identity()
    if 'files' not in request.files:
        return jsonify(create_simple_response("failed", "缺少图片参数", 400))
    files_list = request.files.getlist("files")
    user = db.session.query(User).filter(User.id == current_user_id).first()
    if user is None:
        return jsonify(create_simple_response("failed", "该用户不存在", 400))
    for file in files_list:
        filename = datetime.now().strftime('%Y%m%d_%H%M%S') + ".jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/" + str(current_user_id), filename))
        user.avatar = "/image/" + str(current_user_id) + "/" + filename
        db.session.commit()
    return jsonify(
        create_simple_response("success", "修改头像成功", data="/image/" + str(current_user_id) + "/" + filename))


@app.route("/user/changeUsername", methods=["POST"])
@jwt_required()
def changeUsername():
    current_user_id = get_jwt_identity()
    user = db.session.query(User).filter(User.id == current_user_id).first()
    if user is None:
        return jsonify(create_simple_response("failed", "该用户不存在", 400))
    if "username" not in request.json:
        return jsonify(create_simple_response("failed", "缺少昵称参数", 400))
    username = request.json["username"]
    if username == "":
        return jsonify(create_simple_response("failed", "昵称为空", 400))
    user.username = username
    db.session.commit()
    return jsonify(create_simple_response("success", "修改昵称成功"))


@app.route("/product/<type>")
def getProductByType(type):
    try:
        product_list = db.session.query(Product).filter(Product.type == type).filter(Product.status == 1).order_by(
            db.func.random()).all()
        data = []

        for product in product_list:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score

        for product in product_list:
            tag_counts = Counter([test.tag for test in product.tests])
            product.tag_list = list(tag_counts.keys())
            res = product.to_dict()
            res["tag_list"] = product.tag_list[0:3]
            res["avg_score"] = product.avg_score
            data.append(res)

        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/search/<name>")
def getProductByName(name):
    try:
        product_list = db.session.query(Product).filter(Product.status == 1).filter(
            Product.product_name.like(f'%{name}%')).all()
        data = []

        for product in product_list:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score

        for product in product_list:
            tag_counts = Counter([test.tag for test in product.tests])
            product.tag_list = list(tag_counts.keys())
            res = product.to_dict()
            res["tag_list"] = product.tag_list
            res["avg_score"] = product.avg_score
            data.append(res)

        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route('/generate_qr/<int:id>', methods=['GET'])
def generate_qr(id):
    try:
        # 创建一个QRCode对象
        im = qrcode.make(id)  # 生成二维码
        img = io.BytesIO()  # 创建图片流
        im.save(img, format='PNG')  # 将图片放图片流里面
        img = img.getvalue()  # 返回图片流
        return Response(img, mimetype='image/png')  # 用自定义返回的数据及类型
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/productDetail/<int:id>")
def getProductById(id):
    try:
        product = db.session.query(Product).filter(Product.id == id).first()
        tagDic = {}
        skinScoreDic = {}

        tag_counts = Counter([test.tag for test in product.tests]).items()
        for tag, count in tag_counts:
            tagDic[tag] = count
        res = product.to_dict()
        res["tag_dic"] = tagDic

        # 遍历数据列表
        for item in product.tests:
            # 获取当前的skin_type和score
            skin_type = item.skin_type
            score = item.score
            # 如果skin_type已经在累加器中，则累加score
            if skin_type in skinScoreDic:
                skinScoreDic[skin_type] += score
                # 如果skin_type不在累加器中，则初始化score为当前值
            else:
                skinScoreDic[skin_type] = score

        res["skin_score_dic"] = skinScoreDic

        return jsonify(create_list_response("success", "产品获取成功", data=res))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/productByUser/<int:user_id>")
def getProductByUserId(user_id):
    try:
        product_list = db.session.query(Product).filter(Product.user_id == user_id).all()
        data = [product.to_dict() for product in product_list]
        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/create", methods=["POST"])
@jwt_required()
def createProduct():
    try:
        if "type" not in request.form:
            return jsonify(create_simple_response("failed", "缺少类型参数", 400))
        if "product_name" not in request.form:
            return jsonify(create_simple_response("failed", "缺少名称参数", 400))
        if "start_time" not in request.form:
            return jsonify(create_simple_response("failed", "缺少起始时间参数", 400))
        if "end_time" not in request.form:
            return jsonify(create_simple_response("failed", "缺少结束时间参数", 400))
        if "product_introduce" not in request.form:
            return jsonify(create_simple_response("failed", "缺少简介参数", 400))
        if 'files' not in request.files:
            return jsonify(create_simple_response("failed", "缺少图片参数", 400))
        if 'skin_type' not in request.form:  # "["aa","bb"]"这种类型
            return jsonify(create_simple_response("failed", "缺少肤质类型", 400))
        type = request.form.get("type")
        product_name = request.form.get("product_name")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        product_introduce = request.form.get("product_introduce")
        files_list = request.files.getlist("files")
        print(request.form.get("skin_type"))
        skin_type = ast.literal_eval(request.form.get("skin_type"))  # 将字符转["aa","bb"]转换成列表
        current_user_id = get_jwt_identity()
        if type == "":
            return jsonify(create_simple_response("failed", "肤质类型为空", 400))
        if product_name == "":
            return jsonify(create_simple_response("failed", "产品名称为空", 400))
        if start_time == "":
            return jsonify(create_simple_response("failed", "未设置开始时间", 400))
        if end_time == "":
            return jsonify(create_simple_response("failed", "未设置截止时间", 400))
        if product_introduce == "":
            return jsonify(create_simple_response("failed", "产品介绍为空", 400))
        if len(files_list) == 0:
            return jsonify(create_simple_response("failed", "您未上传任何图片", 400))
        if len(skin_type) == 0:
            return jsonify(create_simple_response("failed", "您未选择任何肤质", 400))

        product = Product(
            type=type,
            product_name=product_name,
            start_time=start_time,
            end_time=end_time,
            user_id=current_user_id,
            product_introduce=product_introduce,
        )

        for file in files_list:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S') + ".jpg"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/" + str(current_user_id), filename))
            product.add_image("/image/" + str(current_user_id) + "/" + filename)

        for skin in skin_type:
            product.add_skin_type(skin)

        db.session.add(product)
        db.session.commit()
        return jsonify(create_simple_response("success", "新建测评成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/notAuditProduct")
@jwt_required()
def getAllNotAuditProduct():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == current_user_id).first()
        if user.permissions != 0:
            return jsonify(create_simple_response("failed", "您不是管理员没有权限访问", 400))
        product_list = db.session.query(Product).filter(Product.status == 2).all()
        # data = [product.to_dict() for product in product_list]
        data = []
        for product in product_list:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score
            res = product.to_dict()
            res["avg_score"] = product.avg_score
            data.append(res)
        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/examProduct", methods=["POST", "PUT"])
@jwt_required()
def examProduct():
    try:
        if "product_id" not in request.json:
            return jsonify(create_simple_response("failed", "缺少产品id参数", 400))
        if "status" not in request.json:
            return jsonify(create_simple_response("failed", "缺少状态参数", 400))
        product_id = request.json["product_id"]
        status = request.json["status"]
        if product_id == "":
            return jsonify(create_simple_response("failed", "您未传递任何产品id", 400))
        if status == "":
            return jsonify(create_simple_response("failed", "您未传递任何产品状态", 400))
        if status == "3":
            return jsonify(create_simple_response("failed", "不允许设置成该状态", 400))
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == current_user_id).first()
        if user.permissions != 0:
            return jsonify(create_simple_response("failed", "您不是管理员没有权限访问", 400))
        product = db.session.query(Product).filter(Product.id == product_id).first()
        if product.status == 3:
            return jsonify(create_simple_response("failed", "该产品状态无法进行审核", 400))
        product.status = status
        product.audit_by = current_user_id
        db.session.commit()
        return jsonify(create_simple_response("success", "修改产品状态成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/product/auditProductBySelf")
@jwt_required()
def getAuditProductBySelf():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id == current_user_id).first()
        if user.permissions != 0:
            return jsonify(create_simple_response("failed", "您不是管理员没有权限访问", 400))
        product_list = db.session.query(Product).filter(Product.audit_by == current_user_id).all()
        res = [product for product in product_list]
        data = []
        for product in res:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score
            res = product.to_dict()
            res["avg_score"] = product.avg_score
            data.append(res)
        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/getJoinedBySelf")
@jwt_required()
def getJoinedProductBySelf():
    try:
        current_user_id = get_jwt_identity()
        joined_list = db.session.query(JoinedTest).filter(JoinedTest.user_id == current_user_id).order_by(
            desc(JoinedTest.id)).all()
        data = []
        res = [joined.product for joined in joined_list]

        for product in res:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score
            res = product.to_dict()
            res["avg_score"] = product.avg_score
            data.append(res)

        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/getPublishedBySelf")
@jwt_required()
def getPublishedProductBySelf():
    try:
        current_user_id = get_jwt_identity()
        product_list = db.session.query(Product).filter(Product.user_id == current_user_id).order_by(
            desc(Product.id)).all()
        data = []
        for product in product_list:
            score = 0
            for test in product.tests:
                score += test.score
            division = len(product.tests)
            if division == 0:
                division = 1
            avg_score = score / division
            product.avg_score = avg_score
            res = product.to_dict()
            res["avg_score"] = product.avg_score
            data.append(res)
        return jsonify(create_list_response("success", "产品获取成功", data=data))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/joinedTest", methods=["POST", "PUT"])
@jwt_required()
def joinedTest():
    try:
        if "product_id" not in request.json:
            return jsonify(create_simple_response("failed", "缺少产品id参数", 400))
        product_id = request.json["product_id"]
        current_user_id = get_jwt_identity()
        project = db.session.query(Product).filter(Product.id == product_id).first()
        if project is None:
            return jsonify(create_simple_response("failed", "该产品不存在", 400))
        if project.status != 3:
            return jsonify(create_simple_response("failed", "该产品已过测评日期", 400))
        get_joined_test = db.session.query(JoinedTest).filter(JoinedTest.user_id == current_user_id).filter(
            JoinedTest.product_id == product_id).first()
        if get_joined_test is not None:
            return jsonify(create_simple_response("failed", "您已加入过该测评", 400))
        joined_test = JoinedTest(user_id=current_user_id, product_id=project.id)
        db.session.add(joined_test)
        db.session.commit()
        return jsonify(create_simple_response("success", "加入测评成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/addTest", methods=["POST", "PUT"])
@jwt_required()
def addTest():
    try:
        current_user_id = get_jwt_identity()
        if "product_id" not in request.form:
            return jsonify(create_simple_response("failed", "缺少产品id参数", 400))
        if "skin_type" not in request.form:
            return jsonify(create_simple_response("failed", "缺少肤质类型参数", 400))
        if "tag" not in request.form:
            return jsonify(create_simple_response("failed", "缺少产品标签参数", 400))
        if "score" not in request.form:
            return jsonify(create_simple_response("failed", "缺少产品测评分数", 400))
        if "feeling" not in request.form:
            return jsonify(create_simple_response("failed", "缺少产品感受参数", 400))
        if 'files' not in request.files:
            return jsonify(create_simple_response("failed", "缺少图片参数", 400))
        product_id = request.form.get("product_id")
        skin_type = request.form.get("skin_type")
        tag = request.form.get("tag")
        score = request.form.get("score")
        feeling = request.form.get("feeling")
        files_list = request.files.getlist("files")
        if product_id == "":
            return jsonify(create_simple_response("failed", "产品id为空", 400))
        if skin_type == "":
            return jsonify(create_simple_response("failed", "测评肤质类型为空", 400))
        if tag == "":
            return jsonify(create_simple_response("failed", "测评标签为空", 400))
        if score == "":
            return jsonify(create_simple_response("failed", "测评分数为空", 400))
        if feeling == "":
            return jsonify(create_simple_response("failed", "测评感受为空", 400))
        if len(files_list) == 0:
            return jsonify(create_simple_response("failed", "您未上传任何图片", 400))
        test = db.session.query(Test).filter(Test.user_id == current_user_id).filter(
            Test.product_id == product_id).first()
        if test is not None:
            return jsonify(create_simple_response("failed", "您已经提交过该产品的测评", 400))
        project = db.session.query(Product).filter(Product.id == product_id).first()
        if project is None:
            return jsonify(create_simple_response("failed", "该产品不存在", 400))
        if project.status != 3:
            return jsonify(create_simple_response("failed", "该产品已过测评日期", 400))
        test = Test(product_id=product_id, skin_type=skin_type, tag=tag, score=score, feeling=feeling,
                    user_id=current_user_id)
        for file in files_list:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S') + ".jpg"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/" + str(current_user_id), filename))
            test.add_image("/image/" + str(current_user_id) + "/" + filename)
        db.session.add(test)
        db.session.commit()
        return jsonify(create_simple_response("success", "提交测评成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/addComment", methods=["POST", "PUT"])
@jwt_required()
def addComment():
    try:
        current_user_id = get_jwt_identity()
        if "product_id" not in request.form:
            return jsonify(create_simple_response("failed", "缺少产品id参数", 400))
        product_id = request.form.get("product_id")
        comment_text = request.form.get("comment_text")
        files_list = request.files.getlist("files")
        if (comment_text is None or comment_text == "") and (len(files_list) == 0 or files_list == []):
            return jsonify(create_simple_response("failed", "您未填写任何评论信息", 400))
        product = db.session.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return jsonify(create_simple_response("failed", "该产品不存在", 400))
        if product.status != 1:
            return jsonify(create_simple_response("failed", "该产品状态不允许评论", 400))
        userComment = UserComment(product_id=product_id, user_id=current_user_id, comment_text=comment_text)

        if len(files_list) != 0 or files_list != []:
            for file in files_list:
                filename = datetime.now().strftime('%Y%m%d_%H%M%S') + ".jpg"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/" + str(current_user_id), filename))
                userComment.add_image("/image/" + str(current_user_id) + "/" + filename)
        db.session.add(userComment)
        db.session.commit()
        return jsonify(create_simple_response("success", "评论成功"))
    except Exception as e:
        return jsonify(create_simple_response("error", str(e), 500))


@app.route("/test/addTextComment", methods=["POST", "PUT"])
@jwt_required()
def addTextComment():
    current_user_id = get_jwt_identity()
    if "product_id" not in request.json:
        return jsonify(create_simple_response("failed", "缺少产品id参数", 400))
    if "comment_text" not in request.json:
        return jsonify(create_simple_response("failed", "缺少产品评论参数", 400))
    product_id = request.json["product_id"]
    comment_text = request.json["comment_text"]
    if product_id == "":
        return jsonify(create_simple_response("failed", "产品id参数为空", 400))
    if comment_text == "":
        return jsonify(create_simple_response("failed", "您为输入任何评论", 400))
    product = db.session.query(Product).filter(Product.id == product_id).first()
    if product is None:
        return jsonify(create_simple_response("failed", "该产品不存在", 400))
    userComment = UserComment(product_id=product_id, user_id=current_user_id, comment_text=comment_text)
    db.session.add(userComment)
    db.session.commit()
    return jsonify(create_simple_response("success", "评论成功"))


def updateProductStatus():
    with app.app_context():
        product_list = db.session.query(Product).filter(Product.status == 3).all()
        current_time = datetime.now()
        for product in product_list:
            date_obj = datetime.strptime(product.end_time, "%Y.%m.%d")
            next_day_obj = date_obj + timedelta(days=1)
            if next_day_obj < current_time:
                product.status = 2
                db.session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(updateProductStatus, 'cron', hour=20, minute=31)  # 这将在每天的00:00运行
scheduler.start()
