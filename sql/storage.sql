use minsys;

-- ----------------------------
-- Procedure structure for `sp_amount`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_amount`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_amount`(IN `BranchID` char(32),IN `SubjectID` char(4) ,IN `TimeStart` datetime,IN `TimeEnd` datetime,OUT `Amount` decimal)
BEGIN
  set TimeStart=date_add(TimeStart,INTERVAL -8 HOUR);
  set TimeEnd=date_add(TimeEnd,INTERVAL -8 HOUR);
	select ifnull(sum(money),0) into Amount from business_subjectbranchchange
  inner join business_ledger on ledger_id=business_ledger.id
  inner join business_bill on business_ledger.bill_id=business_bill.id
  inner join business_subjectbranch on subject_branch_id=business_subjectbranch.id
  where business_ledger.time_gen>TimeStart and business_ledger.time_gen<TimeEnd and business_bill.branch_id=BranchID and subject_id=SubjectID;
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_amount_group_day`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_amount_group_day`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_amount_group_day`(IN `BranchID` char(32),IN `SubjectID` char(4) ,IN `TimeStart` datetime,IN `TimeEnd` datetime)
BEGIN
  set TimeStart=date_add(TimeStart,INTERVAL -8 HOUR);
  set TimeEnd=date_add(TimeEnd,INTERVAL -8 HOUR);
	select CAST(DATE_FORMAT(date_add(business_ledger.time_gen,INTERVAL 8 HOUR), "%e" ) as SIGNED) as d,sum(money) as amount from business_subjectbranchchange
  inner join business_ledger on ledger_id=business_ledger.id
  inner join business_bill on business_ledger.bill_id=business_bill.id
  inner join business_subjectbranch on subject_branch_id=business_subjectbranch.id
  where business_ledger.time_gen>TimeStart and business_ledger.time_gen<TimeEnd and business_bill.branch_id=BranchID and subject_id=SubjectID
  group by d
  order by d;
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_amount_group_hour`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_amount_group_hour`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_amount_group_hour`(IN `BranchID` char(32),IN `SubjectID` char(4) ,IN `TimeStart` datetime,IN `TimeEnd` datetime)
BEGIN
  set TimeStart=date_add(TimeStart,INTERVAL -8 HOUR);
  set TimeEnd=date_add(TimeEnd,INTERVAL -8 HOUR);
	select CAST(DATE_FORMAT(date_add(business_ledger.time_gen,INTERVAL 8 HOUR), "%k" ) as SIGNED) as h,sum(money) as amount from business_subjectbranchchange
  inner join business_ledger on ledger_id=business_ledger.id
  inner join business_bill on business_ledger.bill_id=business_bill.id
  inner join business_subjectbranch on subject_branch_id=business_subjectbranch.id
  where business_ledger.time_gen>TimeStart and business_ledger.time_gen<TimeEnd and business_bill.branch_id=BranchID and subject_id=SubjectID
  group by h
  order by h;
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_amount_group_month`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_amount_group_month`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_amount_group_month`(IN `BranchID` char(32),IN `SubjectID` char(4) ,IN `TimeStart` datetime,IN `TimeEnd` datetime)
BEGIN
  set TimeStart=date_add(TimeStart,INTERVAL -8 HOUR);
  set TimeEnd=date_add(TimeEnd,INTERVAL -8 HOUR);
	select CAST(DATE_FORMAT(date_add(business_ledger.time_gen,INTERVAL 8 HOUR), "%c" ) as SIGNED) as m,sum(money) as amount from business_subjectbranchchange
  inner join business_ledger on ledger_id=business_ledger.id
  inner join business_bill on business_ledger.bill_id=business_bill.id
  inner join business_subjectbranch on subject_branch_id=business_subjectbranch.id
  where business_ledger.time_gen>TimeStart and business_ledger.time_gen<TimeEnd and business_bill.branch_id=BranchID and subject_id=SubjectID
  group by m
  order by m;
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_recharge_times`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_recharge_times`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_recharge_times`(IN bid VARCHAR(32),OUT `flag` INTEGER)
BEGIN
	#处理BillRechargeTimes
	#flag,1 成功,2 没有单据,3 状态不符
	DECLARE t_error INT DEFAULT 0; 
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET t_error=1;
  START TRANSACTION; 

	SET @BillID=bid;

	SELECT business_bill.`status`,cardtimes_id,money,times,branch_id INTO @Status,@CardID,@Money,@Times,@BranchID FROM business_billrechargetimes 
	INNER JOIN business_bill on bill_ptr_id=business_bill.id
	WHERE bill_ptr_id=@BillID;
	
	IF ISNULL(@Status) THEN
	#	SET t_error=1;
		SET flag=2;
	ELSEIF @Status>1 THEN
	#	SET t_error=1;
		SET flag=3;
  ELSE


			#Ledger
			#总账id
			SET @LedgerID=replace(UUID(),'-','');
			#总账时间
			SET @Now=date_add(now(),INTERVAL -8 HOUR);
			#创建总账记录
			INSERT INTO business_ledger (id,bill_id,time_gen) VALUES (@LedgerID,@BillID,@Now);

			SELECT id into @SubjectBranchID FROM business_subjectbranch WHERE branch_id=@BranchID AND subject_id='1001';
			
			#现金变化
			INSERT INTO business_subjectbranchchange(id,ledger_id,subject_branch_id,money) VALUES(replace(UUID(),'-',''),@LedgerID,@SubjectBranchID,@Money);
			#现金余额
			UPDATE business_subjectbranch SET amount=amount+@money WHERE id=@SubjectBranchID;

			#卡变化
			INSERT INTO business_cardtimeschange (id,ledger_id,card_id,times) VALUES(replace(UUID(),'-',''),@LedgerID,@CardID,@Times);
			#卡余额
			UPDATE business_cardtimes SET times=times+@Times WHERE card_ptr_id=@CardID;


			#修改单据状态
			UPDATE business_bill SET status=10 WHERE id=@BillID;

			SET flag=1;
	END IF;


	IF t_error=1 THEN 
		ROLLBACK;
	ELSE 
		COMMIT;
	END IF; 
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_recharge_value`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_recharge_value`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_recharge_value`(IN bid VARCHAR(32),OUT `flag` INTEGER)
BEGIN
	#处理BillRechargeValue
	#flag,1 成功,2 没有单据,3 状态不符
	DECLARE t_error INT DEFAULT 0; 
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET t_error=1;
  START TRANSACTION; 

	SET @BillID=bid;

	SELECT business_bill.`status`,cardvalue_id,money,amount,branch_id INTO @Status,@CardID,@Money,@Amount,@BranchID FROM business_billrechargevalue 
	INNER JOIN business_bill on bill_ptr_id=business_bill.id
	WHERE bill_ptr_id=@BillID;
	
	IF ISNULL(@Status) THEN
	#	SET t_error=1;
		SET flag=2;
	ELSEIF @Status>1 THEN
	#	SET t_error=1;
		SET flag=3;
  ELSE


			#Ledger
			#总账id
			SET @LedgerID=replace(UUID(),'-','');
			#总账时间
			SET @Now=date_add(now(),INTERVAL -8 HOUR);
			#创建总账记录
			INSERT INTO business_ledger (id,bill_id,time_gen) VALUES (@LedgerID,@BillID,@Now);

			SELECT id into @SubjectBranchID FROM business_subjectbranch WHERE branch_id=@BranchID AND subject_id='1001';
			
			#现金变化
			INSERT INTO business_subjectbranchchange(id,ledger_id,subject_branch_id,money) VALUES(replace(UUID(),'-',''),@LedgerID,@SubjectBranchID,@money);
			#现金余额
			UPDATE business_subjectbranch SET amount=amount+@money WHERE id=@SubjectBranchID;

			#卡变化
			INSERT INTO business_cardvaluechange (id,ledger_id,card_id,money) VALUES(replace(UUID(),'-',''),@LedgerID,@CardID,@amount);
			#卡余额
			UPDATE business_cardvalue SET amount=amount+@amount WHERE card_ptr_id=@CardID;


			#修改单据状态
			UPDATE business_bill SET status=10 WHERE id=@BillID;

			SET flag=1;
	END IF;


	IF t_error=1 THEN 
		ROLLBACK;
	ELSE 
		COMMIT;
	END IF; 
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_sale_times`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_sale_times`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_sale_times`(IN bid VARCHAR(32),OUT `flag` INTEGER)
BEGIN
	#处理BillSaleTimes
	#flag,1 成功,2 没有单据,3 状态不符
	DECLARE t_error INT DEFAULT 0; 
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET t_error=1;
  START TRANSACTION; 

	SET @BillID=bid;

	SELECT business_bill.`status`,cardtimes_id,times,branch_id INTO @Status,@CardID,@Times,@BranchID FROM business_billsaletimes
	INNER JOIN business_bill on bill_ptr_id=business_bill.id
	WHERE bill_ptr_id=@BillID;
	
	IF ISNULL(@Status) THEN
		SET t_error=1;
		SET flag=2;
	ELSEIF @Status>1 THEN
		SET t_error=1;
		SET flag=3;
  ELSE


			#Ledger
			#总账id
			SET @LedgerID=replace(UUID(),'-','');
			#总账时间
			SET @Now=date_add(now(),INTERVAL -8 HOUR);
			#创建总账记录
			INSERT INTO business_ledger (id,bill_id,time_gen) VALUES (@LedgerID,@BillID,@Now);

			SELECT id into @SubjectBranchID FROM business_subjectbranch WHERE branch_id=@BranchID AND subject_id='1001';
			

			#卡变化
			INSERT INTO business_cardtimeschange (id,ledger_id,card_id,times) VALUES(replace(UUID(),'-',''),@LedgerID,@CardID,-@Times);
			#卡余额
			UPDATE business_cardtimes SET times=times-@Times WHERE card_ptr_id=@CardID;


			#修改单据状态
			UPDATE business_bill SET status=10 WHERE id=@BillID;

			SET flag=1;
	END IF;


	IF t_error=1 THEN 
		ROLLBACK;
	ELSE 
		COMMIT;
	END IF; 
END
;;
DELIMITER ;

-- ----------------------------
-- Procedure structure for `sp_sale_value`
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_sale_value`;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_sale_value`(IN bid VARCHAR(32),OUT `flag` INTEGER)
BEGIN
	#处理BillSaleValue
	#flag,1 成功,2 没有单据,3 状态不符
	DECLARE t_error INT DEFAULT 0; 
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET t_error=1;
  START TRANSACTION; 

	SET @BillID=bid;

	SELECT business_bill.`status`,cardvalue_id,amount,branch_id INTO @Status,@CardID,@Amount,@BranchID FROM business_billsalevalue
	INNER JOIN business_bill on bill_ptr_id=business_bill.id
	WHERE bill_ptr_id=@BillID;
	
	IF ISNULL(@Status) THEN
		SET t_error=1;
		SET flag=2;
	ELSEIF @Status>1 THEN
		SET t_error=1;
		SET flag=3;
  ELSE


			#Ledger
			#总账id
			SET @LedgerID=replace(UUID(),'-','');
			#总账时间
			SET @Now=date_add(now(),INTERVAL -8 HOUR);
			#创建总账记录
			INSERT INTO business_ledger (id,bill_id,time_gen) VALUES (@LedgerID,@BillID,@Now);

			SELECT id into @SubjectBranchID FROM business_subjectbranch WHERE branch_id=@BranchID AND subject_id='1001';
			

			#卡变化
			INSERT INTO business_cardvaluechange (id,ledger_id,card_id,money) VALUES(replace(UUID(),'-',''),@LedgerID,@CardID,-@amount);
			#卡余额
			UPDATE business_cardvalue SET amount=amount-@amount WHERE card_ptr_id=@CardID;


			#修改单据状态
			UPDATE business_bill SET status=10 WHERE id=@BillID;

			SET flag=1;
	END IF;


	IF t_error=1 THEN 
		ROLLBACK;
	ELSE 
		COMMIT;
	END IF; 
END
;;
DELIMITER ;
