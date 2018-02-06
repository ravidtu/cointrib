from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from .serializer import Loginserializer,InventorySerializer,ModelApprovalSerializer
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from inventory.models import Inventory,ModelApproval
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.parsers import JSONParser

# Create your views here.
"""method to check user"""
def check_user(request,action,view):
    groups = request.user.groups.all().values_list('name', flat=True)
    user_perm= request.user.user_permissions.all().values_list('name', flat=True)
    keyword= action+" "+view
    user_perm=list(filter(lambda x: keyword in x, user_perm))
    if any([i == 'Store Manager' for i in groups]):
        return True
    elif user_perm:
        return True
    else:
        return False


"""class for login api"""
class Login(APIView):
    def post(self, request, format=None):
        serializer = Loginserializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            output=dict()
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user.check_password(password) and user.is_active:
                    token=Token.objects.get_or_create(user=user)
                    output['status']=status.HTTP_200_OK
                    output['usermsg']="Login successful"
                    output['redirect']=serializer.data['redirect_url']
                    output['token']=token[0].key
                    return Response(output,status=status.HTTP_200_OK)
            else:
                output['status'] = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
                output['usermsg'] = "email/password is incorrect"
                return Response(output, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

"""class for inventory GET/POST"""
class InventoryList(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'inventory_list.html'
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    parser_classes = (JSONParser,)
    def list(self, request):
        queryset = self.get_queryset()
        # getting diffrent check based on diffrent user
        store_manager_check = False
        add_perm_check=check_user(request,"add","inventory") #checking add permission
        change_perm_check=check_user(request,"change","inventory") #checking change permission
        delete_perm_check=check_user(request,"delete","inventory") #checking delete permission
        groups = request.user.groups.all().values_list('name', flat=True)
        if any([i == 'Store Manager' for i in groups]):
            store_manager_check = True
        return Response({'inventory': queryset,"store_manager_check":store_manager_check,"add_perm_check":add_perm_check,"change_perm_check":change_perm_check,"delete_perm_check":delete_perm_check})

    def create(self, request, *args, **kwargs):
        if check_user(request,"add","inventory"):
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                output = {"msg": "Inventory Added Successfully"}
                output.update(serializer.data)
                return Response(output, status=status.HTTP_201_CREATED,template_name=None)
            except:
                error_msj=serializer.errors.keys()[0]+" "+serializer.errors[serializer.errors.keys()[0]]
                output = {"msg": error_msj}
                output.update(serializer.data)
                return Response(output)
        else:
            output = {"msg": "You are not authorize to add Inventory"}
            return Response(output)


"""class for inventory PUT/DELETE"""
class InventoryDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    def list(self, request):
        queryset = self.get_queryset()
        return Response({'inventory': queryset},template_name='inventory_list.html')
    def update(self, request, *args, **kwargs):
        if check_user(request,"change","inventory"):
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            output={"msg":str(instance.productName)+" is updated"}
            output.update(serializer.data)
            return Response(output)
        else:
            output = {"msg":"You are not authorize to update Inventory"}
            return Response(output)

    def destroy(self, request, *args, **kwargs):
        if check_user(request,"delete","inventory"):
            instance = self.get_object()
            self.perform_destroy(instance)
            output = {"msg": "Inventory deleted"}
            return Response(output)
        else:
            output = {"msg": "You are not authorize to delete Inventory"}
            return Response(output)

"""Model Approval Class"""
class ApprovModel(generics.ListCreateAPIView,generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ModelApproval.objects.all()
    serializer_class = ModelApprovalSerializer
    def list(self, request):
        queryset = self.get_queryset()
        innerHtml=""
        for approveRequest in queryset:
            if approveRequest.requestedBy != request.user:
                if not approveRequest.approve:
                    button="<button class='btn btn-primary btn-block'onclick=approvePermission("+str(approveRequest.id)+")>Approve</button>"
                else:
                    button="<button class='btn btn-primary btn-block disabled'>Already Approve</button>"

                innerHtml+="<tr><td>"+approveRequest.requestedBy.email+"</td><td>"+approveRequest.action+"</td><td>"+button+"</td></tr>"
                #output.append([approveRequest.requestedBy.email,approveRequest.action,approveRequest.approve])

        html="<table class='table table-striped'><thead><th>email</th><th>action</th><th>Permission</th></thead>" +innerHtml+ "</table>"
        return Response(html)

    def post(self, request, format=None):
        serializer = ModelApprovalSerializer(data=request.data)
        if serializer.is_valid():
            action=serializer.data['action']
            admin_name=serializer.data['admin_name']
            if ContentType.objects.filter(model=admin_name).exists():
                content_id=ContentType.objects.get(model=admin_name)
            else:
                return Response("This model doesn't exist")
            action = action + "_" + admin_name

            if check_user(request,action,admin_name):
                return Response("You already have this permission")

            if not ModelApproval.objects.filter(requestedBy=request.user,action=action,content_type=content_id,approve=0).exists():
                ModelApproval(requestedBy=request.user,action=action,content_type=content_id).save()
                return Response("Approval request has been sent")
            else:
                return Response("You already sent this request")
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
            modlobj=ModelApproval.objects.get(id=pk)
            permisnObj=Permission.objects.get(codename=modlobj.action)
            modlobj.requestedBy.user_permissions.add(permisnObj)
            modlobj.approveBy=request.user.email
            modlobj.approve=1
            modlobj.save()
            return Response("Request Approved")






