# Tests for the KL divergence

import unittest

import torch
from gpytorch.distributions import MultivariateNormal
from gpytorch.metrics import wasserstein


class TestWassersteinDistance(unittest.TestCase):
    def setUp(self):
        self.mean_0 = torch.as_tensor([1, 2])
        self.mean_1 = torch.as_tensor([-1.0, 0.0])
        self.cov_0 = 9.0 * torch.eye(2)
        self.cov_1 = torch.as_tensor([[3, 0.1], [0.1, 3]])
        self.q = MultivariateNormal(self.mean_0, self.cov_0)
        self.p = MultivariateNormal(self.mean_1, self.cov_1)
        self.q_batch = MultivariateNormal(
            mean=torch.stack((self.mean_0, self.mean_0)),
            covariance_matrix=torch.stack((self.cov_0, self.cov_0)),
        )
        self.p_batch = MultivariateNormal(
            mean=torch.stack((self.mean_1, torch.zeros((2,)))),
            covariance_matrix=torch.stack((self.cov_1, 3 * torch.eye(2))),
        )

    def test_same_args_is_zero(self):
        self.assertEqual(wasserstein(self.q, self.q), torch.as_tensor(0.0))

    def test_greater_or_equal_zero(self):
        self.assertGreaterEqual(wasserstein(self.q, self.p).item(), 0.0)

    def test_symmetric(self):
        pass

    def test_batches_of_randvars(self):
        kldivs_batch = wasserstein(self.q_batch, self.p_batch)
        self.assertEqual(kldivs_batch.size()[0], self.q_batch.batch_shape[0])

    def test_wasserstein_univariate_gaussians(self):
        mu_q = torch.as_tensor([-3.0])
        mu_p = torch.as_tensor([0.1])
        sigma_sq_q = torch.as_tensor([[0.2]])
        sigma_sq_p = torch.as_tensor([[1.4]])
        p = MultivariateNormal(mu_p, sigma_sq_p)
        q = MultivariateNormal(mu_q, sigma_sq_q)

        wasserstein_univariate = (
            (mu_q - mu_p) ** 2
            + sigma_sq_q
            + sigma_sq_p
            - 2 * torch.sqrt(sigma_sq_p * sigma_sq_q)
        )
        self.assertAlmostEqual(
            wasserstein(q, p, order=2).item(), wasserstein_univariate.item(), delta=1e-5
        )
