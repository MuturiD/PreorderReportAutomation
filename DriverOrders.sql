declare @string varchar(50)
declare @Longstring varchar(350)
declare @int int


select @string as ContainerCode,@string as ContainerName,UserCode as DSAUserCode,@string as DSAName,@string as AssetNumber,
@Longstring as SalesAreas,count(OrderBatchNumber) as DispatchedOrderCount, @int DispatchedCylPro, @int DispatchedCylSea, @int CompleteOrderCounts,
@int as completcylPro, @int as completcylSea
into #data
from DriverOrderAssignments where Status = 'Pending' group by UserCode
update #data set DSAName = (select top 1 UserFullName from DriverOrderAssignments where DriverOrderAssignments.UserCode = #data.DSAUserCode)
update #data set AssetNumber = (select top 1 AssignedParticularCode from Assignments where Assignments.AssigneeCode = #data.DSAUserCode and Assignments.AssignmentPoint = 'Staff To Asset'
and Status = 'Active')
update #data set ContainerCode = (select top 1 AssignedParticularCode from Assignments where AssignmentPoint = 'Asset To Container'
and Assignments.AssigneeCode = #data.AssetNumber and Assignments.Status = 'Active')
update #data set ContainerName = (select top 1 DistributionPointName from DistributionPoints
where DistributionPoints.DistributionPointCode = #data.ContainerCode)
update #data set AssetNumber = (select top 1 AssetUniqueIdentifier from Assets where Assets.AssetCode = #data.AssetNumber)
update #data set  SalesAreas = (select top 1 container from (select  assigneecode,container=
    stuff(
        (select ','+assignedParticularName
        from assignments a where b.assigneecode=a.assigneecode and assignmentpoint like  '%Staff To Sales Area%'
        FOR XML PATH('')), 1, 1, '') from assignments b where assignmentpoint =  'Staff To Sales Area'  group by assigneecode) a where a.assigneecode=#data.dsauserCode )



update #data set DispatchedCylPro= ( select top 1 DispatchedCylPro  from (
    Select  usercode,sum(quantity)DispatchedCylPro
    from customerorderitems a inner join
    ( select usercode, OrderBatchNumber from DriverOrderAssignments where status='pending' ) b
    on a.batchnumber=b.OrderBatchNumber
    where a.productPackageCode in (select  productPackageCode from productpackages where productPackageName like '%pro%'  )
    group by usercode) a where a.usercode=#data.dsauserCode)


update #data set DispatchedCylSea= ( select top 1 DispatchedCylSea  from (
    Select  usercode,sum(quantity)DispatchedCylSea
    from customerorderitems a inner join
    ( select usercode, OrderBatchNumber from DriverOrderAssignments where status='pending' ) b
    on a.batchnumber=b.OrderBatchNumber
    where a.productPackageCode in (select  productPackageCode from productpackages where productPackageName like '%sea%'  )
    group by usercode) a where a.usercode=#data.dsauserCode)


update #data set CompleteOrderCounts=( select top 1 ordercount from (
        select UserCode as DSAUserCode,count(OrderBatchNumber) as OrderCount from DriverOrderAssignments where Status = 'Complete'
         and cast(deliverydate as date)=cast(getdate() as date)
        group by UserCode ) a where a.DSAUserCode=#data.dsauserCode)


update #data set completcylSea=( select top 1 CompleteCylSea from (
Select  usercode,sum(quantity)CompleteCylSea
    from customerorderitems a inner join
    ( select usercode, OrderBatchNumber from DriverOrderAssignments where status='complete' and cast(deliverydate as date)=cast(getdate() as date) ) b
    on a.batchnumber=b.OrderBatchNumber
    where a.productPackageCode in (select  productPackageCode from productpackages where productPackageName like '%sea%'  )
    group by usercode) a where a.usercode=#data.dsauserCode)



update #data set completcylPro=( select top 1 completcylPro from (
Select  usercode,sum(quantity)completcylPro
    from customerorderitems a inner join
    ( select usercode, OrderBatchNumber from DriverOrderAssignments where status='complete' and cast(deliverydate as date)=cast(getdate() as date) ) b
    on a.batchnumber=b.OrderBatchNumber
    where a.productPackageCode in (select  productPackageCode from productpackages where productPackageName like '%pro%'  )
    group by usercode) a where a.usercode=#data.dsauserCode)


select DSAName, Assetnumber as VregNo, SalesAreas,ContainerName as container,DispatchedOrderCount ,DispatchedCylPro,DispatchedCylSea,Completeordercounts,
completcylPro, completcylSea
from #data order by DispatchedOrderCount desc
