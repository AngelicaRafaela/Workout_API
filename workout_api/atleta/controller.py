from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, params, status, Query, Depends
from pydantic import UUID4
from typing import List, Optional
from fastapi_pagination import Page, paginate, add_pagination, Params

from workout_api.atleta.schemas import (
    AtletaIn,
    AtletaOut,
    AtletaUpdate,
    AtletaOutCustom,
)
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)):
    # Extrai o nome da categoria e do centro de treinamento do corpo da requisição
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    # Busca a categoria correspondente no banco de dados
    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        )
        .scalars()
        .first()
    )

    # Verifica se a categoria foi encontrada
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {categoria_nome} não foi encontrada.",
        )

    # Busca o centro de treinamento correspondente no banco de dados
    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        )
        .scalars()
        .first()
    )

    # Verifica se o centro de treinamento foi encontrado
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento {centro_treinamento_nome} não foi encontrado.",
        )

    try:
        # Cria um novo objeto de atleta para retornar como resposta
        atleta_out = AtletaOut(
            id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
        )
        # Cria um novo objeto de modelo de atleta para inserir no banco de dados
        atleta_model = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )

        # Associa a categoria e o centro de treinamento ao atleta
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        # Adiciona o atleta ao banco de dados
        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError as e:
        # Trata erros de integridade, como CPF duplicado
        await db_session.rollback()
        if "unique constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro de integridade no banco de dados",
        )
    except Exception:
        # Trata outros erros
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco",
        )

    return atleta_out


@router.get(
    "/",
    summary="Consultar todos os Atletas",
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaOutCustom],
)
async def query(
    db_session: DatabaseDependency,
    params: Params = Depends(),  # Adiciona os parâmetros de paginação
    nome: Optional[str] = Query(None, description="Nome do atleta"),
    cpf: Optional[str] = Query(None, description="CPF do atleta"),
) -> Page[AtletaOutCustom]:
    # Constrói a query para consultar os atletas no banco de dados
    query = select(AtletaModel)

    # Aplica filtros de nome e CPF se fornecidos
    if nome:
        query = query.where(AtletaModel.nome == nome)
    if cpf:
        query = query.where(AtletaModel.cpf == cpf)

    # Executa a query e obtém os resultados
    result = await db_session.execute(query)
    atletas = result.scalars().all()

    # Formata os resultados para resposta
    response_data = [
        AtletaOutCustom(
            nome=atleta.nome,
            centro_treinamento=atleta.centro_treinamento.nome,
            categoria=atleta.categoria.nome,
        )
        for atleta in atletas
    ]

    # Retorna os resultados paginados
    return paginate(response_data, params)


add_pagination(router)


@router.get(
    "/{id}",
    summary="Consulta um Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    # Consulta um atleta pelo ID no banco de dados
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    # Verifica se o atleta foi encontrado
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    return atleta


@router.patch(
    "/{id}",
    summary="Editar um Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    # Consulta um atleta pelo ID no banco de dados
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    # Verifica se o atleta foi encontrado
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    # Informações do atleta são atualizadas no banco de dados
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    # Comita as alterações no banco de dados e atualiza o objeto de atleta
    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    "/{id}", summary="Deletar um Atleta pelo id", status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    # Consulta um atleta pelo ID no banco de dados
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    # Verifica se o atleta foi encontrado
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    # Deleta o atleta do banco de dados
    await db_session.delete(atleta)
    await db_session.commit()
