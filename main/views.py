from django.shortcuts import render
from django.shortcuts import render
from pandas.core import api
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from mezzanine.pages.models import Page, RichTextPage, Link
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, logout, login
from rest_framework.authtoken.models import Token
import json
import pandas as pd
from base64 import b64encode, b64decode
from django.conf import settings
from django.core.files.base import ContentFile



# Create your views here.

def advisory_image_location(image_tag):
    try:
        split1 = image_tag.split('src=')[1].split(' ')[0].split('"')[1].split('media')[1]
        return split1
    except Exception as e:
        print(e)
        return ""


def encode_image_to_base64(image_path):
    try:
        image_path = settings.MEDIA_ROOT + image_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            return encoded_image
    except Exception as e:
        print(e)
        return ""



@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_advisory_child_page(request):
    print(request.data)
    project_id = Page.objects.get(title=request.data['project']).id
    if request.data['action'] == 'initial_serve':
        print(request.data['app_language'])
        if request.data['app_language'] == 'English':
            advisory_page = Page.objects.filter(title='ADVISORY_ENGLISH', parent_id=project_id)
        if request.data['app_language'] == 'தமிழ்':
            advisory_page = Page.objects.filter(title='ADVISORY_TAMIL',parent_id=project_id)
        
        child_page = Page.objects.filter(parent=advisory_page).order_by('_order')
        crop_names = child_page.values_list('title', 'richtextpage__content', 'id')
        crop_columns = ['title', 'image_link', 'id']
        crop_df = pd.DataFrame(crop_names, columns=crop_columns)

        crop_df['image_link'] = crop_df.apply(lambda x: advisory_image_location(x['image_link']), axis=1)
        crop_df['image'] = crop_df.apply(lambda x: encode_image_to_base64(x['image_link']), axis=1)

        parent_ids = list(child_page.values_list('id', flat=True))
        crop_level_two_obj = Page.objects.filter(parent_id__in=parent_ids).order_by('_order')
        crop_level_two_list = list(crop_level_two_obj.values_list('id', 'title', 'parent_id'))
        crop_level_two_column = ['id', 'title', 'parent_id']
        crop_level_two_df = pd.DataFrame(crop_level_two_list, columns=crop_level_two_column)
        crop_level_two_dict = crop_level_two_df.groupby('parent_id').apply(lambda x:x.to_dict('r')).to_dict()
        data_dict = {
            'crop_list': crop_df.to_dict('r'),
            'crop_dict': crop_level_two_dict
            }
        return Response(data=data_dict, status=status.HTTP_200_OK)
        
    if request.data['action'] == 'second_level_serve':
        if request.data['app_language'] == 'English':
            advisory_page = Page.objects.filter(title='ADVISORY_ENGLISH', parent_id=project_id)
        if request.data['app_language'] == 'தமிழ்':
            advisory_page = Page.objects.filter(title='ADVISORY_TAMIL', parent_id=project_id)
        try:
            main_page = Page.objects.filter(title=request.data['crop_name'], parent=advisory_page)
            print(main_page)
            advisory_type = Page.objects.filter(parent=main_page, title=request.data['advisory_type'])
            richtext_list = list(advisory_type.values_list('id','title', 'parent', 'parent__title', 'richtextpage__content'))
            richtext_column = ['id', 'title','parent', 'parent_title', 'description']

            richtext_df = pd.DataFrame(richtext_list, columns=richtext_column)
            output_data = richtext_df.groupby('title').apply(lambda x: x.to_dict('r')[0]).to_dict()
            print(output_data)
            return Response(output_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_url_for_pdf_and_video(request):
    filtered_parent_richtext_by_requested_id = RichTextPage.objects.filter(
        id=request.data['title_id'])
    filtered_parent_richtext_ids = filtered_parent_richtext_by_requested_id.values_list(
        'id', flat=True)
    filtered_link = Link.objects.filter(parent=filtered_parent_richtext_ids)
    filtered_link_ids = filtered_link.values_list('id', flat=True)
    links_list = list(filtered_link_ids.values_list('id', 'slug', 'title'))
    links_columns = ['id', 'url', 'type']
    links_df = pd.DataFrame(links_list, columns=links_columns)
    link_dict = {}
    link_dict['images'] = list()
    for index, row in links_df.iterrows():
        if row['type'] == 'url':
            link_dict['url'] = row['url']
        elif row['type'] == 'pdf':
            link_dict['pdf'] = row['url']
        elif row['type'] == 'image':
            # try:
            #     with open(row['url'], 'rb') as image_file:
            #         encoded_image = b64encode(image_file.read())
            #         link_dict['images'].append('data:image/jpeg;base64,' + encoded_image.decode("utf-8"))

            # except Exception as e:
            #     print('Error in Image Encode (Static advisory)', e)

            link_dict['images'].append(row['url'])
    return Response(link_dict)



@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_faq_child_pages(request):
    print(request.data)
    all_pages = Page.objects.all()
    project_id = Page.objects.get(title=request.data['project']).id
    if request.data['app_language'] == 'English':
        if not all_pages.filter(title='FAQ_ENGLISH', parent_id=project_id).exists():
            return Response(data={}, status=status.HTTP_200_OK)
        faq_page = all_pages.get(title='FAQ_ENGLISH', parent_id=project_id)

    if request.data['app_language'] == 'தமிழ்':
        if not all_pages.filter(title='FAQ_TAMIL', parent_id=project_id).exists():
            return Response(data={}, status=status.HTTP_200_OK)
        faq_page = all_pages.get(title='FAQ_TAMIL', parent_id=project_id)

    first_child_pages = all_pages.filter(parent=faq_page).values_list(
        'id', flat=True).order_by('_order')
    second_level_child_pages = Page.objects.filter(
        parent_id__in=first_child_pages).values_list('id', flat=True)
    rich_text_child_pages = RichTextPage.objects.filter(
        page_ptr_id__in=second_level_child_pages)

    richtext_list = list(
        rich_text_child_pages.values_list('id', 'page_ptr', 'page_ptr__title', 'parent', 'parent__title', 'content'))
    richtext_column = ['id', 'page_ptr', 'page_ptr_title',
                       'parent', 'parent_title', 'content']

    richtext_df = pd.DataFrame(richtext_list, columns=richtext_column)

    output_data = richtext_df.groupby('parent_title').apply(
        lambda x: x.to_dict('r')).to_dict()

    return Response(status=status.HTTP_200_OK, data=output_data)



@api_view(['POST'])
def serve_raq_details(request):
    print(request.data)
    all_pages = Page.objects.all()
    project_id = Page.objects.get(title=request.data['project']).id
    raq_page = all_pages.get(title='RAQ', parent_id=project_id)
    first_child_pages = all_pages.filter(parent=raq_page).values_list(
        'id', flat=True).order_by('_order')
    second_level_child_pages = Page.objects.filter(
        parent_id__in=first_child_pages).values_list('id', flat=True)
    rich_text_child_pages = RichTextPage.objects.filter(
        page_ptr_id__in=second_level_child_pages)

    richtext_list = list(
        rich_text_child_pages.values_list('id', 'page_ptr', 'page_ptr__title', 'parent', 'parent__title', 'content'))
    richtext_column = ['id', 'page_ptr', 'page_ptr_title',
                       'parent', 'parent_title', 'content']

    richtext_df = pd.DataFrame(richtext_list, columns=richtext_column)

    output_data = richtext_df.groupby('parent_title').apply(
        lambda x: x.to_dict('r')).to_dict()

    return Response(status=status.HTTP_200_OK, data=output_data)



@api_view(['GET'])
def serve_terms_and_conditions_egavel(request):
    all_pages = Page.objects.all()
    project_id = Page.objects.get(title='Egavel').id

    output_data = all_pages.filter(parent_id=project_id)

    richtext_list = list(
        output_data.values_list('id','title', 'parent', 'parent__title', 'richtextpage__content'))
    richtext_column = ['id', 'title',
                       'parent', 'parent_title', 'description']

    richtext_df = pd.DataFrame(richtext_list, columns=richtext_column)
    output_data = richtext_df.to_dict('r')[0]
   


    return Response(data=output_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_terms_and_conditions_egavel(request):
    post_data = request.data
    richtext_obj = RichTextPage.objects.get(page_ptr_id=post_data['id'])
    richtext_obj.content = post_data['description']
    richtext_obj.save()
    return Response(data=True, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_featured_video_link(request):
    project_id = Page.objects.get(title=request.data['project']).id
    page_obj = Page.objects.get(title='Featured Video', parent_id=project_id)
    data_dict = {
        'video_id': page_obj.description,
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_products_list(request):
    product_obj = Page.objects.filter(title='Products')
    products = Page.objects.filter(parent=product_obj)
    product_ids = products.values_list('id', flat=True)
    richtext_parent = RichTextPage.objects.filter(page_ptr_id__in=product_ids)

    richtext_parent_list = list(richtext_parent.values_list('id', 'parent', 'title', 'content'))
    richtext_parent_column = ['id', 'parent', 'parent_title', 'main_content']
    richtext_parent_df = pd.DataFrame(richtext_parent_list, columns=richtext_parent_column)
    richtext_parent_df

    second_parent = list(richtext_parent.values_list('id',flat=True))
    second_richtext_parent = RichTextPage.objects.filter(parent_id__in=second_parent)
    data_dict = pd.DataFrame(list(second_richtext_parent.values_list('parent_id','parent__title', 'description', 'parent__description')), columns=['id', 'title', 'description', 'image']).to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_publication(request):
    parent_id = Page.objects.get(title=request.data['selected_segment']).id
    publication_obj = Page.objects.filter(parent_id=parent_id)
    publication_list = list(publication_obj.values_list('id', 'title', 'parent_id', 'description'))
    publication_column = ['id', 'title', 'parent_id', 'price']
    publication_df = pd.DataFrame(publication_list, columns=publication_column)
    return Response(data=publication_df.to_dict('r'), status=status.HTTP_200_OK)