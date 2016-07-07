use minsys;
-- ----------------------------
-- Records of business_company
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_company`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_company` AFTER INSERT ON `business_company` FOR EACH ROW begin
    set @cid=new.id;
    select count(*) into @be_maxid from business_maxid where company_id=@cid;
    if @be_maxid=0 then
        insert into business_maxid (id,company_id,branch_max_id,user_max_id,unit_max_id,product_max_id,bill_max_id) values (replace(UUID(),'-',''),@cid,0,0,0,0,0);
    end if;
    select count(*) into @be_csetting from business_companysetting where company_id=@cid;
    if @be_csetting=0 then
        insert into business_companysetting (id,company_id,card_type) values (replace(UUID(),'-',''),@cid,1);
    end if;
end
;;
DELIMITER ;

-- ----------------------------
-- Records of business_branch
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_branch`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_branch` BEFORE INSERT ON `business_branch` FOR EACH ROW begin
    select new.company_id into @cid;
    select branch_max_id into @maxid from business_maxid where company_id=@cid;
    set new.branch_id=LPAD(@maxid+1,3,'0');
    update business_maxid set branch_max_id=@maxid+1 where company_id=@cid;
end
;;
DELIMITER ;

-- ----------------------------
-- Records of business_user
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_user`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_user` BEFORE INSERT ON `business_user` FOR EACH ROW begin
    select new.company_id into @cid;
    select user_max_id into @maxid from business_maxid where company_id=@cid;
    set new.user_id=LPAD(@maxid+1,3,'0');
    update business_maxid set user_max_id=@maxid+1 where company_id=@cid;
end
;;
DELIMITER ;

-- ----------------------------
-- Records of business_unit
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_unit`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_unit` BEFORE INSERT ON `business_unit` FOR EACH ROW begin
    select new.company_id into @cid;
    select unit_max_id into @maxid from business_maxid where company_id=@cid;
    set new.unit_id=INSERT(LPAD(@maxid+1,6,'0'),4,0,'-');
    update business_maxid set unit_max_id=@maxid+1 where company_id=@cid;
end
;;
DELIMITER ;

-- ----------------------------
-- Records of business_product
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_product`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_product` BEFORE INSERT ON `business_product` FOR EACH ROW begin
    select new.company_id into @cid;
    select product_max_id into @maxid from business_maxid where company_id=@cid;
    set new.product_id=INSERT(LPAD(@maxid+1,6,'0'),4,0,'-');
    update business_maxid set product_max_id=@maxid+1 where company_id=@cid;
end
;;
DELIMITER ;

-- ----------------------------
-- Records of business_bill
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_insert_bill`;
DELIMITER ;;
CREATE TRIGGER `tr_insert_bill` BEFORE INSERT ON `business_bill` FOR EACH ROW begin
    select company_id  into @cid from business_branch where id=new.branch_id;
    select bill_max_id into @maxid from business_maxid where company_id=@cid;
    set new.bill_id=INSERT(LPAD(@maxid+1,8,'0'),5,0,'-');
    update business_maxid set bill_max_id=@maxid+1 where company_id=@cid;
end
;;
DELIMITER ;

